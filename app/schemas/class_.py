from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ClassCreate(BaseModel):
    name: str
    grade_level: str
    stream: Optional[str] = None
    academic_year: str
    capacity: int = 40
    room_number: Optional[str] = None
    class_teacher_id: Optional[UUID] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    room_number: Optional[str] = None
    class_teacher_id: Optional[UUID] = None


class ClassResponse(BaseModel):
    id: UUID
    name: str
    grade_level: str
    stream: Optional[str]
    academic_year: str
    capacity: int
    room_number: Optional[str]
    class_teacher_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class TimetableSlotCreate(BaseModel):
    class_id: UUID
    subject_id: UUID
    teacher_id: UUID
    day_of_week: int
    period: int
    start_time: str
    end_time: str
    room: Optional[str] = None


class TimetableSlotResponse(TimetableSlotCreate):
    id: UUID

    class Config:
        from_attributes = True
