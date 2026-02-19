"""
Attendance models for both students and teachers.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, String, ForeignKey, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    HALF_DAY = "half_day"


class StudentAttendance(BaseModel):
    __tablename__ = "student_attendance"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status"),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )
    remarks: Mapped[str | None] = mapped_column(String(200), nullable=True)
    marked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    term: Mapped[str] = mapped_column(String(20), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    class_ = relationship("Class")
    marker = relationship("User", foreign_keys=[marked_by])

    def __repr__(self) -> str:
        return f"<StudentAttendance student={self.student_id} date={self.date} status={self.status}>"


class TeacherAttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_LEAVE = "on_leave"
    HALF_DAY = "half_day"


class TeacherAttendance(BaseModel):
    __tablename__ = "teacher_attendance"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[TeacherAttendanceStatus] = mapped_column(
        Enum(TeacherAttendanceStatus, name="teacher_attendance_status"),
        nullable=False,
        default=TeacherAttendanceStatus.PRESENT,
    )
    time_in: Mapped[str | None] = mapped_column(String(10), nullable=True)    # "07:45"
    time_out: Mapped[str | None] = mapped_column(String(10), nullable=True)   # "16:30"
    leave_type: Mapped[str | None] = mapped_column(String(50), nullable=True) # sick, annual, maternity
    remarks: Mapped[str | None] = mapped_column(String(200), nullable=True)
    marked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    teacher = relationship("Teacher", back_populates="attendance_records")
    marker = relationship("User", foreign_keys=[marked_by])

    def __repr__(self) -> str:
        return f"<TeacherAttendance teacher={self.teacher_id} date={self.date} status={self.status}>"