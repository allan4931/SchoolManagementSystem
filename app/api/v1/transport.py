from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.transport import Bus, TransportRoute, TransportAssignment
from app.schemas.transport import BusCreate, BusResponse, RouteCreate, RouteResponse, AssignTransportRequest

router = APIRouter(prefix="/transport", tags=["Transport"])


@router.get("/buses", response_model=list[BusResponse])
async def list_buses(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_READ)),
):
    r = await db.execute(select(Bus).where(Bus.deleted_at.is_(None)))
    return r.scalars().all()


@router.post("/buses", response_model=BusResponse, status_code=201)
async def add_bus(
    data: BusCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_WRITE)),
):
    bus = Bus(**data.model_dump(), is_synced=False)
    db.add(bus)
    await db.commit()
    await db.refresh(bus)
    return bus


@router.get("/buses/{bus_id}", response_model=BusResponse)
async def get_bus(
    bus_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_READ)),
):
    bus = await db.get(Bus, bus_id)
    if not bus:
        raise HTTPException(404, "Bus not found")
    return bus


@router.put("/buses/{bus_id}", response_model=BusResponse)
async def update_bus(
    bus_id: UUID,
    data: BusCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_WRITE)),
):
    bus = await db.get(Bus, bus_id)
    if not bus:
        raise HTTPException(404, "Bus not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(bus, f, v)
    bus.is_synced = False
    await db.commit()
    await db.refresh(bus)
    return bus


@router.get("/routes", response_model=list[RouteResponse])
async def list_routes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_READ)),
):
    r = await db.execute(select(TransportRoute).where(TransportRoute.deleted_at.is_(None)))
    return r.scalars().all()


@router.post("/routes", response_model=RouteResponse, status_code=201)
async def create_route(
    data: RouteCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_WRITE)),
):
    route = TransportRoute(**data.model_dump(), is_synced=False)
    db.add(route)
    await db.commit()
    await db.refresh(route)
    return route


@router.post("/assign", status_code=201)
async def assign_student(
    data: AssignTransportRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_WRITE)),
):
    existing = await db.execute(
        select(TransportAssignment).where(
            TransportAssignment.student_id == data.student_id,
            TransportAssignment.is_active == True,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Student already assigned to a bus")
    assign = TransportAssignment(**data.model_dump(), is_active=True, is_synced=False)
    db.add(assign)
    await db.commit()
    return {"message": "Student assigned to transport successfully"}


@router.get("/assignments")
async def list_assignments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_READ)),
):
    r = await db.execute(
        select(TransportAssignment).where(
            TransportAssignment.is_active == True,
            TransportAssignment.deleted_at.is_(None),
        )
    )
    return r.scalars().all()


@router.delete("/assignments/{student_id}", status_code=204)
async def remove_assignment(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TRANSPORT_WRITE)),
):
    existing = await db.execute(
        select(TransportAssignment).where(
            TransportAssignment.student_id == student_id,
            TransportAssignment.is_active == True,
        )
    )
    assign = existing.scalar_one_or_none()
    if not assign:
        raise HTTPException(404, "Assignment not found")
    assign.is_active = False
    assign.is_synced = False
    await db.commit()
