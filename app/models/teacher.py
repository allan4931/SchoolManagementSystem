"""
Teacher model — full teacher profile including salary info.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, Numeric, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class TeacherStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    RESIGNED = "resigned"
    RETIRED = "retired"


class Teacher(BaseModel):
    __tablename__ = "teachers"

    teacher_id: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)  # e.g. TCH-2024-001
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Personal info
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(50), nullable=True)
    national_id: Mapped[str | None] = mapped_column(String(30), nullable=True, unique=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Contact
    phone: Mapped[str | None] = mapped_column(String(25), nullable=True)
    alt_phone: Mapped[str | None] = mapped_column(String(25), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Professional info
    specialization: Mapped[str | None] = mapped_column(String(120), nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(200), nullable=True)   # e.g. "BSc Mathematics"
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[TeacherStatus] = mapped_column(
        Enum(TeacherStatus, name="teacher_status"),
        default=TeacherStatus.ACTIVE,
        nullable=False,
    )

    # Salary
    salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(60), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(30), nullable=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    class_assigned = relationship("Class", back_populates="class_teacher", foreign_keys="Class.class_teacher_id")
    subjects = relationship("TeacherSubject", back_populates="teacher", cascade="all, delete-orphan")
    timetable_slots = relationship("TimetableSlot", back_populates="teacher")
    attendance_records = relationship("TeacherAttendance", back_populates="teacher", cascade="all, delete-orphan")
    salary_records = relationship("SalaryRecord", back_populates="teacher", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Teacher {self.teacher_id}: {self.full_name}>"


class SalaryRecord(BaseModel):
    """Monthly salary payment record."""
    __tablename__ = "salary_records"

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    month: Mapped[int] = mapped_column(nullable=False)         # 1–12
    year: Mapped[int] = mapped_column(nullable=False)
    gross_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    deductions: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    net_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    teacher = relationship("Teacher", back_populates="salary_records")
