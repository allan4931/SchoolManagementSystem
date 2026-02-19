from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.exam import Exam, ExamResult
from app.models.student import Student
from app.schemas.exam import ExamCreate, ExamResponse, BulkResultCreate
from app.services.exam_service import create_exam, submit_bulk_results, get_class_ranking
from app.services.pdf_service import generate_report_card
from app.utils.pdf_generator import pdf_response

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("", response_model=list[ExamResponse])
async def list_exams(
    academic_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.EXAM_READ)),
):
    q = select(Exam).where(Exam.deleted_at.is_(None))
    if academic_year:
        q = q.where(Exam.academic_year == academic_year)
    r = await db.execute(q.order_by(Exam.start_date.desc()))
    return r.scalars().all()


@router.post("", response_model=ExamResponse, status_code=201)
async def create_exam_endpoint(
    data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EXAM_WRITE)),
):
    exam = await create_exam(db, data, current_user.id)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.EXAM_READ)),
):
    e = await db.get(Exam, exam_id)
    if not e:
        raise HTTPException(404, "Exam not found")
    return e


@router.post("/{exam_id}/results", status_code=201)
async def enter_results(
    exam_id: UUID,
    data: BulkResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.MARKS_WRITE)),
):
    data.exam_id = exam_id
    results = await submit_bulk_results(db, data, current_user.id)
    await db.commit()
    return {"message": f"Saved {len(results)} results", "count": len(results)}


@router.get("/{exam_id}/results")
async def get_exam_results(
    exam_id: UUID,
    class_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.EXAM_READ)),
):
    q = select(ExamResult).where(
        ExamResult.exam_id == exam_id,
        ExamResult.deleted_at.is_(None),
    )
    if student_id:
        q = q.where(ExamResult.student_id == student_id)
    if class_id:
        q = q.join(Student, ExamResult.student_id == Student.id).where(
            Student.class_id == class_id
        )
    r = await db.execute(q)
    return r.scalars().all()


@router.get("/{exam_id}/ranking/{class_id}")
async def class_ranking(
    exam_id: UUID,
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.EXAM_READ)),
):
    return await get_class_ranking(db, exam_id, class_id)


@router.get("/{exam_id}/report-card/{student_id}")
async def download_report_card(
    exam_id: UUID,
    student_id: UUID,
    class_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.EXAM_READ)),
):
    exam = await db.get(Exam, exam_id)
    student = await db.get(Student, student_id)
    if not exam or not student:
        raise HTTPException(404, "Exam or student not found")
    rankings = await get_class_ranking(db, exam_id, class_id)
    student_rank = next((r for r in rankings if r["student_id"] == student_id), {})
    total_students = len(rankings)
    q = select(ExamResult).where(
        ExamResult.exam_id == exam_id,
        ExamResult.student_id == student_id,
    )
    r = await db.execute(q)
    results_data = [
        {
            "subject_name": str(res.subject_id),
            "marks_obtained": float(res.marks_obtained),
            "max_marks": float(res.max_marks),
            "percentage": res.percentage,
            "grade": res.grade,
            "position": res.position,
            "is_absent": res.is_absent,
            "remarks": res.remarks,
        }
        for res in r.scalars().all()
    ]
    pdf_bytes = generate_report_card(
        student={
            "full_name": student.full_name,
            "student_id": student.student_id,
            "date_of_birth": student.date_of_birth,
            "class_name": str(student.class_id),
        },
        exam={
            "name": exam.name,
            "term": exam.term,
            "academic_year": exam.academic_year,
        },
        results=results_data,
        ranking={
            "rank": student_rank.get("rank", "-"),
            "total_students": total_students,
            "percentage": student_rank.get("percentage", 0),
            "total_marks": student_rank.get("total_marks", 0),
            "total_possible": student_rank.get("total_possible", 0),
        },
    )
    return pdf_response(pdf_bytes, f"report_card_{student.student_id}.pdf")


@router.patch("/{exam_id}/publish")
async def publish_results(
    exam_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.EXAM_WRITE)),
):
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    exam.is_published = True
    exam.is_synced = False
    await db.commit()
    return {"message": "Results published successfully"}
