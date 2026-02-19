"""
Fee service — invoice generation, payment processing, arrears calculation.
"""
import random
import string
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.fee import FeeInvoice, FeeInvoiceItem, FeePayment, FeeStructure, InvoiceStatus
from app.schemas.fee import FeeInvoiceCreate, FeePaymentCreate


def _generate_invoice_number() -> str:
    """Generate unique invoice number like INV-2024-A3F9."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    year = datetime.now().year
    return f"INV-{year}-{suffix}"


def _generate_receipt_number() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"RCT-{suffix}"


async def create_invoice(db: AsyncSession, data: FeeInvoiceCreate, generated_by: UUID) -> FeeInvoice:
    # Calculate total from items
    total = sum(item.amount * item.quantity for item in data.items)

    invoice = FeeInvoice(
        invoice_number=_generate_invoice_number(),
        student_id=data.student_id,
        academic_year=data.academic_year,
        term=data.term,
        issue_date=date.today(),
        due_date=data.due_date,
        total_amount=total,
        paid_amount=0.0,
        discount=data.discount,
        status=InvoiceStatus.UNPAID,
        notes=data.notes,
        generated_by=generated_by,
        is_synced=False,
    )
    db.add(invoice)
    await db.flush()

    for item_data in data.items:
        item = FeeInvoiceItem(
            invoice_id=invoice.id,
            fee_structure_id=item_data.fee_structure_id,
            description=item_data.description,
            amount=item_data.amount,
            quantity=item_data.quantity,
            is_synced=False,
        )
        db.add(item)

    await db.flush()
    return invoice


async def record_payment(db: AsyncSession, data: FeePaymentCreate, received_by: UUID) -> FeePayment:
    result = await db.execute(
        select(FeeInvoice)
        .where(FeeInvoice.id == data.invoice_id)
        .options(selectinload(FeeInvoice.payments))
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.status == InvoiceStatus.PAID:
        raise HTTPException(status_code=400, detail="Invoice is already fully paid")

    remaining = invoice.balance
    if data.amount > remaining + 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Payment ${data.amount} exceeds outstanding balance ${remaining:.2f}",
        )

    payment = FeePayment(
        invoice_id=invoice.id,
        receipt_number=_generate_receipt_number(),
        amount=data.amount,
        payment_date=data.payment_date,
        payment_method=data.payment_method,
        reference_number=data.reference_number,
        received_by=received_by,
        notes=data.notes,
        is_synced=False,
    )
    db.add(payment)

    # Update invoice
    invoice.paid_amount = float(invoice.paid_amount) + data.amount
    if invoice.balance <= 0.01:
        invoice.status = InvoiceStatus.PAID
    else:
        invoice.status = InvoiceStatus.PARTIAL
    invoice.is_synced = False

    await db.flush()
    return payment


async def get_student_arrears(db: AsyncSession, academic_year: Optional[str] = None):
    """Return all students with outstanding balances."""
    query = select(FeeInvoice).where(
        FeeInvoice.status.in_([InvoiceStatus.UNPAID, InvoiceStatus.PARTIAL, InvoiceStatus.OVERDUE]),
        FeeInvoice.deleted_at.is_(None),
    )
    if academic_year:
        query = query.where(FeeInvoice.academic_year == academic_year)

    result = await db.execute(query.options(selectinload(FeeInvoice.student)))
    return result.scalars().all()


async def get_invoice(db: AsyncSession, invoice_id: UUID) -> FeeInvoice:
    result = await db.execute(
        select(FeeInvoice)
        .where(FeeInvoice.id == invoice_id)
        .options(
            selectinload(FeeInvoice.items),
            selectinload(FeeInvoice.payments),
            selectinload(FeeInvoice.student),
        )
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice