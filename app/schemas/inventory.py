from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.inventory import AssetCategory, AssetCondition


class InventoryItemCreate(BaseModel):
    name: str
    asset_tag: Optional[str] = None
    category: AssetCategory = AssetCategory.OTHER
    description: Optional[str] = None
    quantity: int = 1
    unit: Optional[str] = None
    condition: AssetCondition = AssetCondition.GOOD
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    supplier: Optional[str] = None
    warranty_expiry: Optional[date] = None
    serial_number: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    condition: Optional[AssetCondition] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemResponse(BaseModel):
    id: UUID
    name: str
    asset_tag: Optional[str]
    category: AssetCategory
    quantity: int
    condition: AssetCondition
    location: Optional[str]
    purchase_date: Optional[date]
    purchase_price: Optional[float]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceRecordCreate(BaseModel):
    item_id: UUID
    maintenance_date: date
    description: str
    cost: Optional[float] = None
    performed_by: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    condition_after: Optional[AssetCondition] = None
