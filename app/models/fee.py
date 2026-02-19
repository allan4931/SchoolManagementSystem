"""
Fee management models: structures, invoices, payments.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, Numeric, String, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class FeeType(str, enum.Enum):
    TUITION = "tuition"
    TRANSPORT = "transport"
    LIBRARY = "library"
    EXAM = "exam"
    SPORTS = "sports"
    BOARDING = "boarding"
    UNIFORM = "uniform"
    ACTIVITY = "activity"
    OTHER = "other"


class InvoiceStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    WAIVED = "waived"
    OVERDUE = "overdue"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CHEQUE = "cheque"
    OTHER = "other"


class FeeStructure(BaseModel):
    """Defines what fees apply to which class/year/term."""
    __tablename__ = "fee_structures"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    fee_type: Mapped[FeeType] = mapped_column(Enum(FeeType, name="fee_type"), nullable=False)
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True
    )  # NULL = applies to all classes
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False)
    term: Mapped[str] = mapped_column(String(20), nullable=False)
    is_compulsory: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    class_ = relationship("Class", back_populates="fee_structures")
    invoice_items = relationship("FeeInvoiceItem", back_populates="fee_structure")

    def __repr__(self) -> str:
        return f"<FeeStructure {self.name} ${self.amount}>"


class FeeInvoice(BaseModel):
    """Invoice issued to a student for a given term."""
    __tablename__ = "fee_invoices"

    invoice_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    academic_year: Mapped[str] = mapped_column(String(10), nullable=False)
    term: Mapped[str] = mapped_column(String(20), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status"),
        default=InvoiceStatus.UNPAID,
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    @property
    def balance(self) -> float:
        return float(self.total_amount) - float(self.paid_amount) - float(self.discount)

    student = relationship("Student", back_populates="fee_invoices")
    items = relationship("FeeInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("FeePayment", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<FeeInvoice {self.invoice_number} balance={self.balance}>"


class FeeInvoiceItem(BaseModel):
    """Line items on a fee invoice."""
    __tablename__ = "fee_invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fee_invoices.id", ondelete="CASCADE"), nullable=False)
    fee_structure_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fee_structures.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    invoice = relationship("FeeInvoice", back_populates="items")
    fee_structure = relationship("FeeStructure", back_populates="invoice_items")


class FeePayment(BaseModel):
    """Records a payment against an invoice (supports installments)."""
    __tablename__ = "fee_payments"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fee_invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receipt_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method"), nullable=False, default=PaymentMethod.CASH
    )
    reference_number: Mapped[str | None] = mapped_column(String(80), nullable=True)  # bank ref
    received_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_reversed: Mapped[bool] = mapped_column(Boolean, default=False)
    reversal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    invoice = relationship("FeeInvoice", back_populates="payments")
    received_by_user = relationship("User", back_populates="fee_payments_received", foreign_keys=[received_by])

    def __repr__(self) -> str:
        return f"<FeePayment {self.receipt_number} ${self.amount}>"