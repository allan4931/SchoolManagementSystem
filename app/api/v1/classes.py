from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.class_ import Class, TimetableSlot
from app.models.student import Student
from app.schemas.class_ import ClassCreate, ClassUpdate, ClassResponse, TimetableSlotCreate

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=list[ClassResponse])
async def list_classes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_READ)),
):
    r = await db.execute(
        select(Class)
        .where(Class.deleted_at.is_(None))
        .order_by(Class.grade_level, Class.stream)
    )
    return r.scalars().all()


@router.post("", response_model=ClassResponse, status_code=201)
async def create_class(
    data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    c = Class(**data.model_dump(), is_synced=False)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_READ)),
):
    c = await db.get(Class, class_id)
    if not c:
        raise HTTPException(404, "Class not found")
    return c


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: UUID,
    data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    c = await db.get(Class, class_id)
    if not c:
        raise HTTPException(404, "Class not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(c, f, v)
    c.is_synced = False
    await db.commit()
    await db.refresh(c)
    return c


@router.delete("/{class_id}", status_code=204)
async def delete_class(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    c = await db.get(Class, class_id)
    if not c:
        raise HTTPException(404, "Class not found")
    c.soft_delete()
    await db.commit()


@router.get("/{class_id}/students")
async def get_class_students(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_READ)),
):
    r = await db.execute(
        select(Student)
        .where(Student.class_id == class_id, Student.deleted_at.is_(None))
        .order_by(Student.last_name)
    )
    return r.scalars().all()


@router.get("/{class_id}/timetable")
async def get_timetable(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_READ)),
):
    r = await db.execute(
        select(TimetableSlot)
        .where(TimetableSlot.class_id == class_id)
        .order_by(TimetableSlot.day_of_week, TimetableSlot.period)
    )
    return r.scalars().all()


@router.post("/{class_id}/timetable", status_code=201)
async def add_timetable_slot(
    class_id: UUID,
    data: TimetableSlotCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    slot = TimetableSlot(**data.model_dump(), is_synced=False)
    db.add(slot)
    await db.commit()
    return {"message": "Timetable slot added"}


@router.delete("/{class_id}/timetable/{slot_id}", status_code=204)
async def delete_timetable_slot(
    class_id: UUID,
    slot_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_WRITE)),
):
    slot = await db.get(TimetableSlot, slot_id)
    if not slot:
        raise HTTPException(404, "Slot not found")
    await db.delete(slot)
    await db.commit()
