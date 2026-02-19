"""
PDF generation service using ReportLab.
Generates: fee receipts, student report cards, attendance reports.
"""
import io
from datetime import date
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.config import settings


def _school_header(elements: list, styles) -> None:
    """Add school letterhead to document."""
    elements.append(Paragraph(settings.SCHOOL_NAME, styles["SchoolName"]))
    elements.append(Paragraph(settings.SCHOOL_ADDRESS, styles["SubTitle"]))
    elements.append(Paragraph(settings.SCHOOL_PHONE, styles["SubTitle"]))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    elements.append(Spacer(1, 5 * mm))


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SchoolName", fontSize=16, alignment=TA_CENTER,
        fontName="Helvetica-Bold", textColor=colors.darkblue, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="SubTitle", fontSize=9, alignment=TA_CENTER,
        fontName="Helvetica", textColor=colors.grey, spaceAfter=1
    ))
    styles.add(ParagraphStyle(
        name="DocTitle", fontSize=13, alignment=TA_CENTER,
        fontName="Helvetica-Bold", textColor=colors.black, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="FieldLabel", fontSize=9, fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="FieldValue", fontSize=9, fontName="Helvetica"
    ))
    return styles


def generate_fee_receipt(payment: dict, invoice: dict, student: dict) -> bytes:
    """
    Generate a printable PDF receipt for a fee payment.
    Accepts plain dicts for flexibility (from API response or ORM objects).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = _get_styles()
    elements = []

    _school_header(elements, styles)

    elements.append(Paragraph("OFFICIAL FEE RECEIPT", styles["DocTitle"]))
    elements.append(Spacer(1, 5 * mm))

    # Receipt info table
    receipt_data = [
        ["Receipt No:", payment.get("receipt_number", ""), "Date:", str(payment.get("payment_date", date.today()))],
        ["Student:", student.get("full_name", ""), "Class:", student.get("class_name", "")],
        ["Student ID:", student.get("student_id", ""), "Academic Year:", invoice.get("academic_year", "")],
        ["Term:", invoice.get("term", ""), "Invoice No:", invoice.get("invoice_number", "")],
    ]
    info_table = Table(receipt_data, colWidths=[3.5 * cm, 7 * cm, 2.5 * cm, 5 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 5 * mm))

    # Payment detail
    elements.append(Paragraph("Payment Details", styles["FieldLabel"]))
    elements.append(Spacer(1, 2 * mm))

    detail_data = [["Description", "Amount"]]
    for item in invoice.get("items", []):
        detail_data.append([item.get("description", ""), f"${item.get('amount', 0):.2f}"])

    detail_data.append(["", ""])
    detail_data.append(["Total Invoice Amount", f"${invoice.get('total_amount', 0):.2f}"])
    detail_data.append(["Amount Paid (This Receipt)", f"${payment.get('amount', 0):.2f}"])
    detail_data.append(["Outstanding Balance", f"${invoice.get('balance', 0):.2f}"])

    detail_table = Table(detail_data, colWidths=[13 * cm, 5 * cm])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -4), [colors.white, colors.lightgrey]),
        ("LINEABOVE", (0, -3), (-1, -3), 1, colors.darkblue),
        ("FONTNAME", (0, -3), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, 0), 1, colors.white),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 8 * mm))

    # Payment method
    elements.append(Paragraph(
        f"Payment Method: <b>{payment.get('payment_method', 'Cash').upper()}</b>",
        styles["FieldValue"]
    ))
    elements.append(Spacer(1, 8 * mm))

    # Signature area
    sig_data = [["____________________________", "", "____________________________"],
                ["Cashier Signature", "", "Official Stamp"]]
    sig_table = Table(sig_data, colWidths=[7 * cm, 4 * cm, 7 * cm])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph(
        "This is a computer-generated receipt and is valid without a signature.",
        ParagraphStyle("footer", fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(elements)
    return buffer.getvalue()


def generate_report_card(student: dict, exam: dict, results: list[dict], ranking: dict) -> bytes:
    """Generate a student academic report card PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = _get_styles()
    elements = []

    _school_header(elements, styles)
    elements.append(Paragraph("STUDENT ACADEMIC REPORT CARD", styles["DocTitle"]))
    elements.append(Paragraph(f"{exam.get('name', '')} — {exam.get('term', '')} {exam.get('academic_year', '')}", styles["SubTitle"]))
    elements.append(Spacer(1, 5 * mm))

    # Student Info
    info_data = [
        ["Name:", student.get("full_name", ""), "Class:", student.get("class_name", "")],
        ["Student ID:", student.get("student_id", ""), "Form Position:", f"{ranking.get('rank', '-')} / {ranking.get('total_students', '-')}"],
        ["Date of Birth:", str(student.get("date_of_birth", "")), "Percentage:", f"{ranking.get('percentage', 0):.1f}%"],
    ]
    info_table = Table(info_data, colWidths=[3 * cm, 7.5 * cm, 3 * cm, 5 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightblue),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#e8f4fd"), colors.white]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    # Results table
    elements.append(Paragraph("Academic Results", styles["FieldLabel"]))
    elements.append(Spacer(1, 2 * mm))

    result_data = [["Subject", "Max Marks", "Marks Obtained", "Percentage", "Grade", "Position", "Remarks"]]
    for r in results:
        result_data.append([
            r.get("subject_name", ""),
            f"{r.get('max_marks', 100):.0f}",
            "ABS" if r.get("is_absent") else f"{r.get('marks_obtained', 0):.1f}",
            "—" if r.get("is_absent") else f"{r.get('percentage', 0):.1f}%",
            r.get("grade", ""),
            str(r.get("position", "—")),
            r.get("remarks", ""),
        ])

    result_table = Table(result_data, colWidths=[4.5*cm, 2*cm, 2.5*cm, 2.5*cm, 1.5*cm, 2*cm, 3.5*cm])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 6 * mm))

    # Summary
    summary_data = [
        ["Total Marks:", f"{ranking.get('total_marks', 0):.1f} / {ranking.get('total_possible', 0):.0f}",
         "Overall %:", f"{ranking.get('percentage', 0):.2f}%",
         "Class Position:", f"{ranking.get('rank', '-')}"],
    ]
    summary_table = Table(summary_data, colWidths=[3*cm, 4*cm, 2.5*cm, 3*cm, 3*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8 * mm))

    # Grading key
    grade_key = [["Grade Key:", "A+(90-100)", "A(80-89)", "B(70-79)", "C(60-69)", "D(50-59)", "E(40-49)", "F(<40)"]]
    grade_table = Table(grade_key)
    grade_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.darkblue),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elements.append(grade_table)
    elements.append(Spacer(1, 8 * mm))

    # Signatures
    sig_data = [
        ["____________________", "____________________", "____________________"],
        ["Class Teacher", "Headmaster", "Parent/Guardian"],
        [f"Date: _______________", f"Date: _______________", f"Date: _______________"],
    ]
    sig_table = Table(sig_data, colWidths=[6*cm, 6*cm, 6*cm])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return buffer.getvalue()