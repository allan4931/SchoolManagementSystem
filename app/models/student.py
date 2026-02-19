"""
Student model — complete student profile with guardian, medical, and academic history.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, String, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentStatus(str, enum.Enum):
    ACTIVE = "active"
    TRANSFERRED = "transferred"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"
    EXPELLED = "expelled"
    DECEASED = "deceased"


class Student(BaseModel):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(25), unique=True, nullable=False, index=True)  # STU-2024-001

    # Personal Information
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender_enum"), nullable=False)
    nationality: Mapped[str | None] = mapped_column(String(60), nullable=True)
    national_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    birth_certificate_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    religion: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Academic
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="SET NULL"),
        nullable=True,
    )
    admission_date: Mapped[date] = mapped_column(Date, nullable=False)
    admission_number: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[StudentStatus] = mapped_column(
        Enum(StudentStatus, name="student_status"),
        default=StudentStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    previous_school: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Guardian / Parent Information
    guardian_name: Mapped[str] = mapped_column(String(120), nullable=False)
    guardian_phone: Mapped[str] = mapped_column(String(25), nullable=False)
    guardian_alt_phone: Mapped[str | None] = mapped_column(String(25), nullable=True)
    guardian_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    guardian_relationship: Mapped[str | None] = mapped_column(String(50), nullable=True)   # Father, Mother, etc.
    guardian_occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guardian_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Emergency Contact
    emergency_contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(25), nullable=True)

    # Medical Information
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    medical_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    disability: Mapped[str | None] = mapped_column(String(200), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    doctor_phone: Mapped[str | None] = mapped_column(String(25), nullable=True)

    # Transport
    uses_school_transport: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)

    # Relationships
    class_ = relationship("Class", back_populates="students", foreign_keys=[class_id])
    attendance_records = relationship("StudentAttendance", back_populates="student", cascade="all, delete-orphan")
    fee_invoices = relationship("FeeInvoice", back_populates="student", cascade="all, delete-orphan")
    exam_results = relationship("ExamResult", back_populates="student", cascade="all, delete-orphan")
    library_issues = relationship("LibraryIssue", back_populates="student", cascade="all, delete-orphan")
    transport_assignment = relationship("TransportAssignment", back_populates="student", uselist=False)
    transfer_records = relationship("TransferRecord", back_populates="student", cascade="all, delete-orphan")
    suspension_records = relationship("SuspensionRecord", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Student {self.student_id}: {self.full_name}>"


class TransferRecord(BaseModel):
    """Records when a student transfers to/from another school."""
    __tablename__ = "transfer_records"

    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    transfer_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "in" | "out"
    transfer_date: Mapped[date] = mapped_column(Date, nullable=False)
    from_school: Mapped[str | None] = mapped_column(String(200), nullable=True)
    to_school: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    student = relationship("Student", back_populates="transfer_records")


class SuspensionRecord(BaseModel):
    """Records student suspensions."""
    __tablename__ = "suspension_records"

    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    issued_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reinstated: Mapped[bool] = mapped_column(Boolean, default=False)
    reinstatement_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    student = relationship("Student", back_populates="suspension_records")