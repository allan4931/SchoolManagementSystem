from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.attendance import StudentAttendance, TeacherAttendance, AttendanceStatus
from app.schemas.attendance import StudentAttendanceCreate, TeacherAttendanceCreate, BulkStudentAttendance

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/students", status_code=201)
async def mark_student_attendance(
    data: StudentAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ATTENDANCE_WRITE)),
):
    existing = await db.execute(
        select(StudentAttendance).where(
            StudentAttendance.student_id == data.student_id,
            StudentAttendance.date == data.date,
        )
    )
    rec = existing.scalar_one_or_none()
    if rec:
        rec.status = data.status
        rec.remarks = data.remarks
        rec.is_synced = False
    else:
        rec = StudentAttendance(
            **data.model_dump(),
            marked_by=current_user.id,
            is_synced=False,
        )
        db.add(rec)
    await db.commit()
    return {"message": "Attendance marked", "status": data.status}


@router.post("/students/bulk", status_code=201)
async def bulk_mark_attendance(
    data: BulkStudentAttendance,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ATTENDANCE_WRITE)),
):
    saved = 0
    for record in data.records:
        existing = await db.execute(
            select(StudentAttendance).where(
                StudentAttendance.student_id == record["student_id"],
                StudentAttendance.date == data.date,
            )
        )
        rec = existing.scalar_one_or_none()
        if rec:
            rec.status = record.get("status", "present")
            rec.is_synced = False
        else:
            att = StudentAttendance(
                student_id=record["student_id"],
                class_id=data.class_id,
                date=data.date,
                status=record.get("status", "present"),
                remarks=record.get("remarks"),
                term=data.term,
                academic_year=data.academic_year,
                marked_by=current_user.id,
                is_synced=False,
            )
            db.add(att)
        saved += 1
    await db.commit()
    return {"message": f"Marked attendance for {saved} students"}


@router.get("/students/report")
async def student_attendance_report(
    class_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    term: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ATTENDANCE_READ)),
):
    q = select(StudentAttendance).where(StudentAttendance.deleted_at.is_(None))
    if class_id:
        q = q.where(StudentAttendance.class_id == class_id)
    if student_id:
        q = q.where(StudentAttendance.student_id == student_id)
    if start_date:
        q = q.where(StudentAttendance.date >= start_date)
    if end_date:
        q = q.where(StudentAttendance.date <= end_date)
    if term:
        q = q.where(StudentAttendance.term == term)
    r = await db.execute(q.order_by(StudentAttendance.date.desc()).limit(500))
    records = r.scalars().all()
    if student_id:
        total = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
        absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        late = sum(1 for r in records if r.status == AttendanceStatus.LATE)
        excused = sum(1 for r in records if r.status == AttendanceStatus.EXCUSED)
        pct = round((present / total * 100), 2) if total else 0
        return {
            "summary": {
                "total_days": total,
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
                "attendance_percentage": pct,
            },
            "records": records,
        }
    return records


@router.post("/teachers", status_code=201)
async def mark_teacher_attendance(
    data: TeacherAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ATTENDANCE_WRITE)),
):
    existing = await db.execute(
        select(TeacherAttendance).where(
            TeacherAttendance.teacher_id == data.teacher_id,
            TeacherAttendance.date == data.date,
        )
    )
    rec = existing.scalar_one_or_none()
    if rec:
        for f, v in data.model_dump(exclude_unset=True).items():
            setattr(rec, f, v)
        rec.is_synced = False
    else:
        rec = TeacherAttendance(
            **data.model_dump(),
            marked_by=current_user.id,
            is_synced=False,
        )
        db.add(rec)
    await db.commit()
    return {"message": "Teacher attendance marked"}


@router.get("/teachers/report")
async def teacher_attendance_report(
    teacher_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ATTENDANCE_READ)),
):
    q = select(TeacherAttendance).where(TeacherAttendance.deleted_at.is_(None))
    if teacher_id:
        q = q.where(TeacherAttendance.teacher_id == teacher_id)
    if start_date:
        q = q.where(TeacherAttendance.date >= start_date)
    if end_date:
        q = q.where(TeacherAttendance.date <= end_date)
    r = await db.execute(q.order_by(TeacherAttendance.date.desc()).limit(500))
    return r.scalars().all()
