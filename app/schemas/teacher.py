from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.teacher import TeacherStatus


class TeacherCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    alt_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    hire_date: Optional[date] = None
    salary: Optional[float] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    tax_id: Optional[str] = None


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    salary: Optional[float] = None
    status: Optional[TeacherStatus] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None


class TeacherResponse(BaseModel):
    id: UUID
    teacher_id: str
    first_name: str
    last_name: str
    full_name: str
    gender: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    specialization: Optional[str]
    qualification: Optional[str]
    hire_date: Optional[date]
    status: TeacherStatus
    salary: Optional[float]
    photo_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubjectAssignRequest(BaseModel):
    subject_id: UUID
    class_id: Optional[UUID] = None
    academic_year: str


class SalaryRecordCreate(BaseModel):
    teacher_id: UUID
    month: int
    year: int
    gross_salary: float
    deductions: float = 0.0
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None