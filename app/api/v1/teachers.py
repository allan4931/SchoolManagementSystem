from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, File, UploadFile, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.teacher import Teacher, SalaryRecord, TeacherStatus
from app.models.subject import TeacherSubject
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate, SubjectAssignRequest, SalaryRecordCreate
from app.utils.file_upload import save_photo
from app.utils.pagination import paginate

router = APIRouter(prefix="/teachers", tags=["Teachers"])


def gen_teacher_id(year: int, count: int) -> str:
    return f"TCH-{year}-{count:04d}"


@router.get("")
async def list_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    search: Optional[str] = None,
    status: Optional[TeacherStatus] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_READ)),
):
    q = select(Teacher).where(Teacher.deleted_at.is_(None))
    if status:
        q = q.where(Teacher.status == status)
    if search:
        t = f"%{search}%"
        q = q.where(
            Teacher.first_name.ilike(t) |
            Teacher.last_name.ilike(t) |
            Teacher.teacher_id.ilike(t)
        )
    count = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.offset(skip).limit(limit).order_by(Teacher.last_name))
    return paginate(result.scalars().all(), count, skip, limit)


@router.post("", status_code=201, response_model=TeacherResponse)
async def create_teacher(
    data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_WRITE)),
):
    year = datetime.now().year
    count = (await db.execute(select(func.count(Teacher.id)))).scalar_one() + 1
    teacher = Teacher(
        **data.model_dump(),
        teacher_id=gen_teacher_id(year, count),
        is_synced=False,
    )
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_READ)),
):
    t = await db.get(Teacher, teacher_id)
    if not t:
        raise HTTPException(404, "Teacher not found")
    return t


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: UUID,
    data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_WRITE)),
):
    t = await db.get(Teacher, teacher_id)
    if not t:
        raise HTTPException(404, "Teacher not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(t, f, v)
    t.is_synced = False
    await db.commit()
    await db.refresh(t)
    return t


@router.delete("/{teacher_id}", status_code=204)
async def delete_teacher(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_DELETE)),
):
    t = await db.get(Teacher, teacher_id)
    if not t:
        raise HTTPException(404, "Teacher not found")
    t.soft_delete()
    await db.commit()


@router.post("/{teacher_id}/photo")
async def upload_teacher_photo(
    teacher_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_WRITE)),
):
    t = await db.get(Teacher, teacher_id)
    if not t:
        raise HTTPException(404, "Teacher not found")
    t.photo_url = await save_photo(file, "teachers")
    t.is_synced = False
    await db.commit()
    return {"photo_url": t.photo_url}


@router.post("/{teacher_id}/subjects", status_code=201)
async def assign_subject(
    teacher_id: UUID,
    data: SubjectAssignRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_WRITE)),
):
    ts = TeacherSubject(
        teacher_id=teacher_id,
        subject_id=data.subject_id,
        class_id=data.class_id,
        academic_year=data.academic_year,
        is_synced=False,
    )
    db.add(ts)
    await db.commit()
    return {"message": "Subject assigned successfully"}


@router.get("/{teacher_id}/subjects")
async def get_teacher_subjects(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_READ)),
):
    result = await db.execute(
        select(TeacherSubject).where(TeacherSubject.teacher_id == teacher_id)
    )
    return result.scalars().all()


@router.post("/{teacher_id}/salary", status_code=201)
async def add_salary_record(
    teacher_id: UUID,
    data: SalaryRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TEACHER_WRITE)),
):
    net = data.gross_salary - data.deductions
    rec = SalaryRecord(
        **data.model_dump(),
        net_salary=net,
        paid_by=current_user.id,
        is_synced=False,
    )
    db.add(rec)
    await db.commit()
    return {"message": "Salary record added", "net_salary": net}


@router.get("/{teacher_id}/salary")
async def get_salary_records(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TEACHER_READ)),
):
    result = await db.execute(
        select(SalaryRecord)
        .where(SalaryRecord.teacher_id == teacher_id)
        .order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc())
    )
    return result.scalars().all()
