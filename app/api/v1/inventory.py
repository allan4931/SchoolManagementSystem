from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.inventory import InventoryItem, MaintenanceRecord, AssetCategory
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    MaintenanceRecordCreate,
)
from app.utils.pagination import paginate

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryItemResponse])
async def list_inventory(
    category: Optional[AssetCategory] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.INVENTORY_READ)),
):
    q = select(InventoryItem).where(
        InventoryItem.deleted_at.is_(None),
        InventoryItem.is_active == True,
    )
    if category:
        q = q.where(InventoryItem.category == category)
    if search:
        q = q.where(InventoryItem.name.ilike(f"%{search}%"))
    count = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    r = await db.execute(q.offset(skip).limit(limit).order_by(InventoryItem.name))
    return paginate(r.scalars().all(), count, skip, limit)


@router.post("", response_model=InventoryItemResponse, status_code=201)
async def add_item(
    data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    item = InventoryItem(**data.model_dump(), added_by=current_user.id, is_synced=False)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.INVENTORY_READ)),
):
    item = await db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_item(
    item_id: UUID,
    data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    item = await db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(item, f, v)
    item.is_synced = False
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
async def deactivate_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    item = await db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    item.is_active = False
    item.is_synced = False
    await db.commit()


@router.post("/{item_id}/maintenance", status_code=201)
async def add_maintenance(
    item_id: UUID,
    data: MaintenanceRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    rec = MaintenanceRecord(
        **data.model_dump(),
        recorded_by=current_user.id,
        is_synced=False,
    )
    db.add(rec)
    if data.condition_after:
        item = await db.get(InventoryItem, item_id)
        if item:
            item.condition = data.condition_after
            item.is_synced = False
    await db.commit()
    return {"message": "Maintenance record added"}


@router.get("/{item_id}/maintenance")
async def item_maintenance_history(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.INVENTORY_READ)),
):
    r = await db.execute(
        select(MaintenanceRecord)
        .where(MaintenanceRecord.item_id == item_id)
        .order_by(MaintenanceRecord.maintenance_date.desc())
    )
    return r.scalars().all()
