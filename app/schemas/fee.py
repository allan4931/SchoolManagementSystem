from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.models.fee import FeeType, InvoiceStatus, PaymentMethod


class FeeStructureCreate(BaseModel):
    name: str
    fee_type: FeeType
    class_id: Optional[UUID] = None
    amount: float
    academic_year: str
    term: str
    is_compulsory: bool = True
    description: Optional[str] = None


class FeeStructureResponse(BaseModel):
    id: UUID
    name: str
    fee_type: FeeType
    class_id: Optional[UUID]
    amount: float
    academic_year: str
    term: str
    is_compulsory: bool

    class Config:
        from_attributes = True


class FeeInvoiceItemCreate(BaseModel):
    fee_structure_id: Optional[UUID] = None
    description: str
    amount: float
    quantity: int = 1


class FeeInvoiceCreate(BaseModel):
    student_id: UUID
    academic_year: str
    term: str
    due_date: date
    discount: float = 0.0
    notes: Optional[str] = None
    items: List[FeeInvoiceItemCreate]


class FeeInvoiceResponse(BaseModel):
    id: UUID
    invoice_number: str
    student_id: UUID
    academic_year: str
    term: str
    issue_date: date
    due_date: date
    total_amount: float
    paid_amount: float
    discount: float
    balance: float
    status: InvoiceStatus

    class Config:
        from_attributes = True


class FeePaymentCreate(BaseModel):
    invoice_id: UUID
    amount: float
    payment_date: date
    payment_method: PaymentMethod = PaymentMethod.CASH
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class FeePaymentResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    receipt_number: str
    amount: float
    payment_date: date
    payment_method: PaymentMethod
    reference_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ArrearsReport(BaseModel):
    student_id: UUID
    student_name: str
    student_class: Optional[str]
    total_invoiced: float
    total_paid: float
    total_balance: float
    invoices: List[FeeInvoiceResponse]