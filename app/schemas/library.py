from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    isbn: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None
    category: Optional[str] = None
    subject_id: Optional[UUID] = None
    shelf_location: Optional[str] = None
    total_copies: int = 1
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None
    description: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    shelf_location: Optional[str] = None
    total_copies: Optional[int] = None


class BookResponse(BaseModel):
    id: UUID
    title: str
    isbn: Optional[str]
    author: Optional[str]
    publisher: Optional[str]
    category: Optional[str]
    shelf_location: Optional[str]
    total_copies: int
    available_copies: int
    created_at: datetime

    class Config:
        from_attributes = True


class IssueBookRequest(BaseModel):
    book_id: UUID
    student_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    due_date: date
    fine_per_day: float = 0.50
    condition_on_issue: Optional[str] = "Good"


class ReturnBookRequest(BaseModel):
    issue_id: UUID
    condition_on_return: Optional[str] = None
    notes: Optional[str] = None


class LibraryIssueResponse(BaseModel):
    id: UUID
    book_id: UUID
    student_id: Optional[UUID]
    teacher_id: Optional[UUID]
    issue_date: date
    due_date: date
    return_date: Optional[date]
    is_returned: bool
    days_overdue: int
    fine_amount: float
    fine_paid: bool

    class Config:
        from_attributes = True
