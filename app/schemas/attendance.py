from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.attendance import AttendanceStatus, TeacherAttendanceStatus


class StudentAttendanceCreate(BaseModel):
    student_id: UUID
    class_id: UUID
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None
    term: str
    academic_year: str


class BulkStudentAttendance(BaseModel):
    class_id: UUID
    date: date
    term: str
    academic_year: str
    records: List[dict]


class AttendanceResponse(BaseModel):
    id: UUID
    student_id: UUID
    class_id: UUID
    date: date
    status: AttendanceStatus
    remarks: Optional[str]
    term: str
    academic_year: str
    created_at: datetime

    class Config:
        from_attributes = True


class TeacherAttendanceCreate(BaseModel):
    teacher_id: UUID
    date: date
    status: TeacherAttendanceStatus
    time_in: Optional[str] = None
    time_out: Optional[str] = None
    leave_type: Optional[str] = None
    remarks: Optional[str] = None


class AttendanceSummary(BaseModel):
    total_days: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_percentage: float
