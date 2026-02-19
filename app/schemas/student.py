from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from app.models.student import Gender, StudentStatus


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Gender
    nationality: Optional[str] = None
    national_id: Optional[str] = None
    birth_certificate_no: Optional[str] = None
    religion: Optional[str] = None
    class_id: Optional[UUID] = None
    admission_date: date
    academic_year: str
    previous_school: Optional[str] = None

    # Guardian
    guardian_name: str
    guardian_phone: str
    guardian_alt_phone: Optional[str] = None
    guardian_email: Optional[EmailStr] = None
    guardian_relationship: Optional[str] = None
    guardian_occupation: Optional[str] = None
    guardian_address: Optional[str] = None

    # Emergency
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    # Medical
    blood_group: Optional[str] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    disability: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None

    uses_school_transport: bool = False

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, v):
        if v and v not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            raise ValueError("Invalid blood group")
        return v


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    class_id: Optional[UUID] = None
    status: Optional[StudentStatus] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[EmailStr] = None
    guardian_address: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    uses_school_transport: Optional[bool] = None


class StudentResponse(BaseModel):
    id: UUID
    student_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str]
    full_name: str
    date_of_birth: Optional[date]
    gender: Gender
    nationality: Optional[str]
    photo_url: Optional[str]
    class_id: Optional[UUID]
    admission_date: date
    academic_year: str
    status: StudentStatus
    guardian_name: str
    guardian_phone: str
    guardian_email: Optional[str]
    blood_group: Optional[str]
    uses_school_transport: bool
    created_at: datetime
    is_synced: bool

    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[StudentResponse]


class TransferRecordCreate(BaseModel):
    transfer_type: str  # "in" | "out"
    transfer_date: date
    from_school: Optional[str] = None
    to_school: Optional[str] = None
    reason: Optional[str] = None


class SuspensionRecordCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str