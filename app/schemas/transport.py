from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.transport import BusStatus


class BusCreate(BaseModel):
    registration_number: str
    bus_number: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity: int = 30
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_license: Optional[str] = None
    insurance_expiry: Optional[date] = None


class BusResponse(BaseModel):
    id: UUID
    registration_number: str
    bus_number: str
    make: Optional[str]
    model: Optional[str]
    capacity: int
    status: BusStatus
    driver_name: Optional[str]
    driver_phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    name: str
    bus_id: UUID
    description: Optional[str] = None
    stops: Optional[str] = None
    morning_departure: Optional[str] = None
    afternoon_departure: Optional[str] = None
    monthly_fee: float = 0.0


class RouteResponse(BaseModel):
    id: UUID
    name: str
    bus_id: UUID
    description: Optional[str]
    stops: Optional[str]
    morning_departure: Optional[str]
    monthly_fee: float
    is_active: bool

    class Config:
        from_attributes = True


class AssignTransportRequest(BaseModel):
    student_id: UUID
    bus_id: UUID
    route_id: UUID
    pickup_point: Optional[str] = None
    start_date: date
