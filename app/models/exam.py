"""
Exam management: exams, marks, grading, rankings.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, Numeric, String, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class ExamType(str, enum.Enum):
    MID_TERM = "mid_term"
    END_TERM = "end_term"
    MOCK = "mock"
    CONTINUOUS = "continuous_assessment"
    ENTRANCE = "entrance"
    SUPPLEMENTARY = "supplementary"


class Exam(BaseModel):
    __tablename__ = "exams"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    exam_type: Mapped[ExamType] = mapped_column(Enum(ExamType, name="exam_type"), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False)
    term: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)  # results visible to teachers?
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")
    schedules = relationship("ExamSchedule", back_populates="exam", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Exam {self.name} ({self.academic_year} {self.term})>"


class ExamSchedule(BaseModel):
    """Per-subject exam timetable."""
    __tablename__ = "exam_schedules"

    exam_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    max_marks: Mapped[float] = mapped_column(Numeric(5, 2), default=100.0)
    pass_marks: Mapped[float] = mapped_column(Numeric(5, 2), default=50.0)
    invigilator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=True)

    exam = relationship("Exam", back_populates="schedules")
    subject = relationship("Subject")
    class_ = relationship("Class")


class ExamResult(BaseModel):
    __tablename__ = "exam_results"

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    marks_obtained: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    max_marks: Mapped[float] = mapped_column(Numeric(6, 2), default=100.0)
    grade: Mapped[str | None] = mapped_column(String(5), nullable=True)     # A+, A, B, etc.
    points: Mapped[int | None] = mapped_column(Integer, nullable=True)      # for ranking
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)    # rank in class for this subject
    remarks: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_absent: Mapped[bool] = mapped_column(Boolean, default=False)
    entered_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    @property
    def percentage(self) -> float:
        if self.max_marks == 0:
            return 0.0
        return round((float(self.marks_obtained) / float(self.max_marks)) * 100, 2)

    exam = relationship("Exam", back_populates="results")
    student = relationship("Student", back_populates="exam_results")
    subject = relationship("Subject", back_populates="exam_results")
    entered_by_user = relationship("User", foreign_keys=[entered_by])

    def __repr__(self) -> str:
        return f"<ExamResult student={self.student_id} exam={self.exam_id} {self.grade}>"