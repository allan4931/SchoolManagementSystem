"""
Class (Form/Grade) model — represents a school class like "Form 3A".
"""
import uuid
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Class(BaseModel):
    __tablename__ = "classes"

    name: Mapped[str] = mapped_column(String(60), nullable=False)           # e.g. "Form 3A"
    grade_level: Mapped[str] = mapped_column(String(30), nullable=False)    # e.g. "Form 3"
    stream: Mapped[str | None] = mapped_column(String(10), nullable=True)   # e.g. "A", "B"
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g. "2024"
    capacity: Mapped[int] = mapped_column(Integer, default=40)
    room_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Class teacher FK — nullable because teacher may not be assigned yet
    class_teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    class_teacher = relationship("Teacher", back_populates="class_assigned", foreign_keys=[class_teacher_id])
    students = relationship("Student", back_populates="class_", foreign_keys="Student.class_id")
    timetable_slots = relationship("TimetableSlot", back_populates="class_", cascade="all, delete-orphan")
    fee_structures = relationship("FeeStructure", back_populates="class_")

    def __repr__(self) -> str:
        return f"<Class {self.name} ({self.academic_year})>"


class TimetableSlot(BaseModel):
    __tablename__ = "timetable_slots"

    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)   # 0=Mon, 4=Fri
    period: Mapped[int] = mapped_column(Integer, nullable=False)        # 1-8
    start_time: Mapped[str] = mapped_column(String(10), nullable=False) # "08:00"
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)   # "08:45"
    room: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Relationships
    class_ = relationship("Class", back_populates="timetable_slots")
    subject = relationship("Subject", back_populates="timetable_slots")
    teacher = relationship("Teacher", back_populates="timetable_slots")