from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.fee import FeeStructure, FeeInvoice, FeePayment
from app.schemas.fee import (
    FeeStructureCreate, FeeStructureResponse,
    FeeInvoiceCreate, FeeInvoiceResponse,
    FeePaymentCreate, FeePaymentResponse,
)
from app.services.fee_service import create_invoice, record_payment, get_student_arrears, get_invoice
from app.services.pdf_service import generate_fee_receipt
from app.utils.pdf_generator import pdf_response

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("/structures", response_model=list[FeeStructureResponse])
async def list_fee_structures(
    academic_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.FEE_READ)),
):
    q = select(FeeStructure).where(FeeStructure.deleted_at.is_(None))
    if academic_year:
        q = q.where(FeeStructure.academic_year == academic_year)
    r = await db.execute(q.order_by(FeeStructure.name))
    return r.scalars().all()


@router.post("/structures", response_model=FeeStructureResponse, status_code=201)
async def create_fee_structure(
    data: FeeStructureCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.FEE_WRITE)),
):
    fs = FeeStructure(**data.model_dump(), is_synced=False)
    db.add(fs)
    await db.commit()
    await db.refresh(fs)
    return fs


@router.post("/invoices", response_model=FeeInvoiceResponse, status_code=201)
async def generate_invoice(
    data: FeeInvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.FEE_WRITE)),
):
    inv = await create_invoice(db, data, current_user.id)
    await db.commit()
    await db.refresh(inv)
    return inv


@router.get("/invoices/{invoice_id}", response_model=FeeInvoiceResponse)
async def get_invoice_detail(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.FEE_READ)),
):
    return await get_invoice(db, invoice_id)


@router.get("/student/{student_id}/invoices")
async def student_invoices(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.FEE_READ)),
):
    r = await db.execute(
        select(FeeInvoice)
        .where(FeeInvoice.student_id == student_id)
        .order_by(FeeInvoice.issue_date.desc())
    )
    return r.scalars().all()


@router.post("/payments", response_model=FeePaymentResponse, status_code=201)
async def make_payment(
    data: FeePaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.FEE_WRITE)),
):
    payment = await record_payment(db, data, current_user.id)
    await db.commit()
    await db.refresh(payment)
    return payment


@router.get("/payments/{payment_id}/receipt")
async def download_receipt(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.FEE_READ)),
):
    from sqlalchemy.orm import selectinload
    r = await db.execute(
        select(FeePayment)
        .where(FeePayment.id == payment_id)
        .options(selectinload(FeePayment.invoice))
    )
    payment = r.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")
    invoice = await get_invoice(db, payment.invoice_id)
    from app.models.student import Student
    student = await db.get(Student, invoice.student_id)
    pdf_bytes = generate_fee_receipt(
        payment={
            "receipt_number": payment.receipt_number,
            "amount": float(payment.amount),
            "payment_date": payment.payment_date,
            "payment_method": payment.payment_method,
        },
        invoice={
            "invoice_number": invoice.invoice_number,
            "total_amount": float(invoice.total_amount),
            "balance": invoice.balance,
            "academic_year": invoice.academic_year,
            "term": invoice.term,
            "items": [
                {"description": i.description, "amount": float(i.amount)}
                for i in invoice.items
            ],
        },
        student={
            "full_name": student.full_name if student else "",
            "student_id": student.student_id if student else "",
        },
    )
    return pdf_response(pdf_bytes, f"receipt_{payment.receipt_number}.pdf")


@router.get("/arrears")
async def arrears_report(
    academic_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.FEE_READ)),
):
    return await get_student_arrears(db, academic_year)
