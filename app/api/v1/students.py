"""
Student management endpoints.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.student import (
    StudentCreate, StudentResponse, StudentUpdate,
    StudentListResponse, TransferRecordCreate, SuspensionRecordCreate,
)
from app.services import student_service
from app.utils.file_upload import save_photo
from app.utils.pagination import paginate
from app.models.student import StudentStatus

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=StudentListResponse)
async def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    class_id: Optional[UUID] = Query(None),
    status: Optional[StudentStatus] = Query(None),
    academic_year: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_READ)),
):
    students, total = await student_service.get_students(
        db, skip=skip, limit=limit,
        class_id=class_id, status=status,
        search=search, academic_year=academic_year,
    )
    return paginate(students, total, skip, limit)


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    student = await student_service.create_student(db, data, current_user.id)
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_READ)),
):
    return await student_service.get_student(db, student_id)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: UUID,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    student = await student_service.update_student(db, student_id, data)
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_DELETE)),
):
    await student_service.soft_delete_student(db, student_id)
    await db.commit()


@router.post("/{student_id}/photo", response_model=StudentResponse)
async def upload_photo(
    student_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    photo_url = await save_photo(file, subfolder="students")
    student = await student_service.update_photo(db, student_id, photo_url)
    await db.commit()
    await db.refresh(student)
    return student


@router.post("/{student_id}/transfer", status_code=201)
async def add_transfer(
    student_id: UUID,
    data: TransferRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    record = await student_service.add_transfer_record(db, student_id, data, current_user.id)
    await db.commit()
    return {"message": "Transfer record added", "id": str(record.id)}


@router.post("/{student_id}/suspend", status_code=201)
async def suspend_student(
    student_id: UUID,
    data: SuspensionRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.STUDENT_WRITE)),
):
    record = await student_service.add_suspension_record(db, student_id, data, current_user.id)
    await db.commit()
    return {"message": "Suspension record added", "id": str(record.id)}