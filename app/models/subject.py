"""
Subject model — school subjects like Math, English, etc.
Also handles teacher-subject and class-subject assignments.
"""
import uuid
from sqlalchemy import Boolean, String, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Subject(BaseModel):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)   # e.g. "MTH101"
    department: Mapped[str | None] = mapped_column(String(80), nullable=True)    # e.g. "Sciences"
    is_elective: Mapped[bool] = mapped_column(Boolean, default=False)
    max_marks: Mapped[float] = mapped_column(Numeric(5, 2), default=100.0)
    pass_mark: Mapped[float] = mapped_column(Numeric(5, 2), default=50.0)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    credit_hours: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    teacher_subjects = relationship("TeacherSubject", back_populates="subject", cascade="all, delete-orphan")
    exam_results = relationship("ExamResult", back_populates="subject")
    timetable_slots = relationship("TimetableSlot", back_populates="subject")

    def __repr__(self) -> str:
        return f"<Subject {self.code}: {self.name}>"


class TeacherSubject(BaseModel):
    """Association table: which teacher teaches which subject in which class."""
    __tablename__ = "teacher_subjects"

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False, default="2024")

    # Relationships
    teacher = relationship("Teacher", back_populates="subjects")
    subject = relationship("Subject", back_populates="teacher_subjects")
    class_ = relationship("Class")