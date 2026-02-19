"""
Student service — all business logic for student operations.
"""
import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.student import Student, TransferRecord, SuspensionRecord, StudentStatus
from app.schemas.student import StudentCreate, StudentUpdate, TransferRecordCreate, SuspensionRecordCreate


async def generate_student_id(db: AsyncSession, academic_year: str) -> str:
    """Generate sequential student ID like STU-2024-001."""
    year = academic_year[:4]
    result = await db.execute(
        select(func.count(Student.id)).where(
            Student.academic_year == academic_year,
            Student.deleted_at.is_(None)
        )
    )
    count = result.scalar_one() + 1
    return f"STU-{year}-{count:04d}"


async def create_student(db: AsyncSession, data: StudentCreate, created_by: UUID) -> Student:
    student_id = await generate_student_id(db, data.academic_year)
    student = Student(
        **data.model_dump(),
        student_id=student_id,
        is_synced=False,
    )
    db.add(student)
    await db.flush()
    return student


async def get_student(db: AsyncSession, student_id: UUID) -> Student:
    result = await db.execute(
        select(Student)
        .where(Student.id == student_id, Student.deleted_at.is_(None))
        .options(selectinload(Student.class_))
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


async def get_students(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    class_id: Optional[UUID] = None,
    status: Optional[StudentStatus] = None,
    search: Optional[str] = None,
    academic_year: Optional[str] = None,
) -> tuple[list[Student], int]:
    query = select(Student).where(Student.deleted_at.is_(None))

    if class_id:
        query = query.where(Student.class_id == class_id)
    if status:
        query = query.where(Student.status == status)
    if academic_year:
        query = query.where(Student.academic_year == academic_year)
    if search:
        term = f"%{search}%"
        query = query.where(
            Student.first_name.ilike(term) |
            Student.last_name.ilike(term) |
            Student.student_id.ilike(term) |
            Student.guardian_phone.ilike(term)
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.offset(skip).limit(limit).order_by(Student.last_name, Student.first_name)
    result = await db.execute(query)
    return result.scalars().all(), total


async def update_student(db: AsyncSession, student_id: UUID, data: StudentUpdate) -> Student:
    student = await get_student(db, student_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    student.is_synced = False
    await db.flush()
    return student


async def soft_delete_student(db: AsyncSession, student_id: UUID) -> None:
    student = await get_student(db, student_id)
    student.soft_delete()


async def update_photo(db: AsyncSession, student_id: UUID, photo_url: str) -> Student:
    student = await get_student(db, student_id)
    student.photo_url = photo_url
    student.is_synced = False
    await db.flush()
    return student


async def add_transfer_record(
    db: AsyncSession, student_id: UUID, data: TransferRecordCreate, user_id: UUID
) -> TransferRecord:
    student = await get_student(db, student_id)

    record = TransferRecord(
        student_id=student_id,
        approved_by=user_id,
        **data.model_dump(),
    )
    db.add(record)

    if data.transfer_type == "out":
        student.status = StudentStatus.TRANSFERRED
        student.is_synced = False

    await db.flush()
    return record


async def add_suspension_record(
    db: AsyncSession, student_id: UUID, data: SuspensionRecordCreate, user_id: UUID
) -> SuspensionRecord:
    student = await get_student(db, student_id)

    record = SuspensionRecord(
        student_id=student_id,
        issued_by=user_id,
        **data.model_dump(),
    )
    db.add(record)
    student.status = StudentStatus.SUSPENDED
    student.is_synced = False
    await db.flush()
    return record