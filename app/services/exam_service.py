"""
Exam service — marks entry, automatic grading, class ranking.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.exam import Exam, ExamResult, ExamSchedule
from app.models.student import Student
from app.schemas.exam import BulkResultCreate, ExamCreate


# ── Grading Scale (customisable per school) ───────────────────────────────────
GRADE_SCALE = [
    (90, 100, "A+", 1),
    (80,  89, "A",  2),
    (70,  79, "B",  3),
    (60,  69, "C",  4),
    (50,  59, "D",  5),
    (40,  49, "E",  6),
    (0,   39, "F",  7),
]


def calculate_grade(marks: float, max_marks: float) -> tuple[str, int]:
    """Return (letter_grade, grade_points) for a given mark."""
    if max_marks == 0:
        return "N/A", 0
    pct = (marks / max_marks) * 100
    for low, high, grade, pts in GRADE_SCALE:
        if low <= pct <= high:
            return grade, pts
    return "F", 7


async def create_exam(db: AsyncSession, data: ExamCreate, created_by: UUID) -> Exam:
    exam = Exam(**data.model_dump(), created_by=created_by, is_synced=False)
    db.add(exam)
    await db.flush()
    return exam


async def submit_bulk_results(db: AsyncSession, data: BulkResultCreate, entered_by: UUID) -> list[ExamResult]:
    """Save results for multiple students, auto-calculating grade and points."""
    # Verify exam exists
    exam = await db.get(Exam, data.exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    saved = []
    for r in data.results:
        # Check for existing result (prevent duplicates)
        existing = await db.execute(
            select(ExamResult).where(
                ExamResult.exam_id == data.exam_id,
                ExamResult.student_id == r.student_id,
                ExamResult.subject_id == r.subject_id,
            )
        )
        existing_result = existing.scalar_one_or_none()

        grade, points = calculate_grade(r.marks_obtained, r.max_marks)

        if existing_result:
            existing_result.marks_obtained = r.marks_obtained
            existing_result.max_marks = r.max_marks
            existing_result.grade = grade if not r.is_absent else "ABS"
            existing_result.points = points if not r.is_absent else None
            existing_result.is_absent = r.is_absent
            existing_result.remarks = r.remarks
            existing_result.entered_by = entered_by
            existing_result.is_synced = False
            saved.append(existing_result)
        else:
            result = ExamResult(
                exam_id=data.exam_id,
                student_id=r.student_id,
                subject_id=r.subject_id,
                marks_obtained=r.marks_obtained,
                max_marks=r.max_marks,
                grade=grade if not r.is_absent else "ABS",
                points=points if not r.is_absent else None,
                is_absent=r.is_absent,
                remarks=r.remarks,
                entered_by=entered_by,
                is_synced=False,
            )
            db.add(result)
            saved.append(result)

    await db.flush()
    await _recalculate_positions(db, data.exam_id)
    return saved


async def _recalculate_positions(db: AsyncSession, exam_id: UUID) -> None:
    """Recompute per-subject positions after marks entry."""
    results_q = await db.execute(
        select(ExamResult).where(
            ExamResult.exam_id == exam_id,
            ExamResult.is_absent == False,
        )
    )
    results = results_q.scalars().all()

    # Group by subject
    by_subject: dict[UUID, list[ExamResult]] = {}
    for r in results:
        by_subject.setdefault(r.subject_id, []).append(r)

    for subject_id, subject_results in by_subject.items():
        sorted_results = sorted(subject_results, key=lambda x: float(x.marks_obtained), reverse=True)
        for rank, r in enumerate(sorted_results, 1):
            r.position = rank

    await db.flush()


async def get_class_ranking(db: AsyncSession, exam_id: UUID, class_id: UUID) -> list[dict]:
    """Return ranked list of students for a given exam and class."""
    # Get all results for students in this class
    results_q = await db.execute(
        select(ExamResult)
        .join(Student, ExamResult.student_id == Student.id)
        .where(
            ExamResult.exam_id == exam_id,
            Student.class_id == class_id,
            ExamResult.deleted_at.is_(None),
        )
        .options(selectinload(ExamResult.student), selectinload(ExamResult.subject))
    )
    results = results_q.scalars().all()

    # Group by student
    by_student: dict[UUID, list[ExamResult]] = {}
    for r in results:
        by_student.setdefault(r.student_id, []).append(r)

    rankings = []
    for student_id, student_results in by_student.items():
        total_marks = sum(float(r.marks_obtained) for r in student_results if not r.is_absent)
        total_possible = sum(float(r.max_marks) for r in student_results)
        total_points = sum(r.points for r in student_results if r.points)
        pct = (total_marks / total_possible * 100) if total_possible else 0

        rankings.append({
            "student_id": student_id,
            "student_name": student_results[0].student.full_name if student_results else "",
            "total_marks": total_marks,
            "total_possible": total_possible,
            "percentage": round(pct, 2),
            "total_points": total_points,
            "subjects": student_results,
        })

    # Sort by total marks descending
    rankings.sort(key=lambda x: x["total_marks"], reverse=True)
    for i, entry in enumerate(rankings, 1):
        entry["rank"] = i

    return rankings