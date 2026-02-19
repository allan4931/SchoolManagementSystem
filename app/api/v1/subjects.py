from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=list[SubjectResponse])
async def list_subjects(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_READ)),
):
    r = await db.execute(
        select(Subject)
        .where(Subject.deleted_at.is_(None))
        .order_by(Subject.name)
    )
    return r.scalars().all()


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(
    data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    existing = await db.execute(
        select(Subject).where(Subject.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Subject code '{data.code}' already exists")
    s = Subject(**data.model_dump(), is_synced=False)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_READ)),
):
    s = await db.get(Subject, subject_id)
    if not s:
        raise HTTPException(404, "Subject not found")
    return s


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: UUID,
    data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    s = await db.get(Subject, subject_id)
    if not s:
        raise HTTPException(404, "Subject not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(s, f, v)
    s.is_synced = False
    await db.commit()
    await db.refresh(s)
    return s


@router.delete("/{subject_id}", status_code=204)
async def delete_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    s = await db.get(Subject, subject_id)
    if not s:
        raise HTTPException(404, "Subject not found")
    s.soft_delete()
    await db.commit()
