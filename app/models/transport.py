"""
Transport management: buses, routes, student assignments.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, Numeric, String, ForeignKey, Text, Boolean, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class BusStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class Bus(BaseModel):
    __tablename__ = "buses"

    registration_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    bus_number: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "Bus 01"
    make: Mapped[str | None] = mapped_column(String(60), nullable=True)  # Toyota
    model: Mapped[str | None] = mapped_column(String(60), nullable=True) # Coaster
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    status: Mapped[BusStatus] = mapped_column(Enum(BusStatus, name="bus_status"), default=BusStatus.ACTIVE)
    driver_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    driver_phone: Mapped[str | None] = mapped_column(String(25), nullable=True)
    driver_license: Mapped[str | None] = mapped_column(String(40), nullable=True)
    insurance_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_service_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    routes = relationship("TransportRoute", back_populates="bus")
    assignments = relationship("TransportAssignment", back_populates="bus")

    def __repr__(self) -> str:
        return f"<Bus {self.bus_number} ({self.registration_number})>"


class TransportRoute(BaseModel):
    __tablename__ = "transport_routes"

    name: Mapped[str] = mapped_column(String(120), nullable=False)       # e.g. "Northern Route"
    bus_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buses.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stops: Mapped[str | None] = mapped_column(Text, nullable=True)       # JSON list of stop names
    morning_departure: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "06:30"
    afternoon_departure: Mapped[str | None] = mapped_column(String(10), nullable=True)
    monthly_fee: Mapped[float] = mapped_column(Numeric(8, 2), default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bus = relationship("Bus", back_populates="routes")
    assignments = relationship("TransportAssignment", back_populates="route")

    def __repr__(self) -> str:
        return f"<TransportRoute {self.name}>"


class TransportAssignment(BaseModel):
    """Links a student to a bus route."""
    __tablename__ = "transport_assignments"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    bus_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("buses.id"), nullable=False)
    route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transport_routes.id"), nullable=False)
    pickup_point: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    student = relationship("Student", back_populates="transport_assignment")
    bus = relationship("Bus", back_populates="assignments")
    route = relationship("TransportRoute", back_populates="assignments")