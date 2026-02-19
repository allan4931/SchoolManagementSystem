from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.models.exam import ExamType


class ExamCreate(BaseModel):
    name: str
    exam_type: ExamType
    academic_year: str
    term: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ExamResponse(BaseModel):
    id: UUID
    name: str
    exam_type: ExamType
    academic_year: str
    term: str
    start_date: Optional[date]
    end_date: Optional[date]
    is_published: bool

    class Config:
        from_attributes = True


class ExamResultCreate(BaseModel):
    student_id: UUID
    subject_id: UUID
    marks_obtained: float
    max_marks: float = 100.0
    is_absent: bool = False
    remarks: Optional[str] = None


class BulkResultCreate(BaseModel):
    """Submit results for multiple students at once."""
    exam_id: UUID
    results: List[ExamResultCreate]


class ExamResultResponse(BaseModel):
    id: UUID
    exam_id: UUID
    student_id: UUID
    subject_id: UUID
    marks_obtained: float
    max_marks: float
    percentage: float
    grade: Optional[str]
    points: Optional[int]
    position: Optional[int]
    is_absent: bool
    remarks: Optional[str]

    class Config:
        from_attributes = True


class StudentRanking(BaseModel):
    rank: int
    student_id: UUID
    student_name: str
    total_marks: float
    total_possible: float
    percentage: float
    average_grade: str
    subjects: List[ExamResultResponse]