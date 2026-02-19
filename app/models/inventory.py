"""
Inventory management: school assets, equipment tracking.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, Numeric, String, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class AssetCondition(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"
    DISPOSED = "disposed"


class AssetCategory(str, enum.Enum):
    FURNITURE = "furniture"
    ELECTRONICS = "electronics"
    SPORTS = "sports"
    LABORATORY = "laboratory"
    STATIONERY = "stationery"
    BUILDING = "building"
    VEHICLE = "vehicle"
    OTHER = "other"


class InventoryItem(BaseModel):
    __tablename__ = "inventory_items"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    asset_tag: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)  # e.g. "IT-001"
    category: Mapped[AssetCategory] = mapped_column(
        Enum(AssetCategory, name="asset_category"), nullable=False, default=AssetCategory.OTHER
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)  # e.g. "pieces", "sets"
    condition: Mapped[AssetCondition] = mapped_column(
        Enum(AssetCondition, name="asset_condition"), default=AssetCondition.GOOD
    )
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "Lab 1", "Store"
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    warranty_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    added_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    maintenance_records = relationship("MaintenanceRecord", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<InventoryItem {self.asset_tag}: {self.name}>"


class MaintenanceRecord(BaseModel):
    """Tracks maintenance/repair history of an asset."""
    __tablename__ = "maintenance_records"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False
    )
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    next_maintenance_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    condition_after: Mapped[AssetCondition | None] = mapped_column(
        Enum(AssetCondition, name="asset_condition"), nullable=True
    )
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    item = relationship("InventoryItem", back_populates="maintenance_records")