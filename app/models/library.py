"""
Library system: book catalogue, issuing, returns, fines.
"""
import uuid
import enum
from datetime import date
from sqlalchemy import Date, Enum, Numeric, String, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class BookStatus(str, enum.Enum):
    AVAILABLE = "available"
    ISSUED = "issued"
    RESERVED = "reserved"
    DAMAGED = "damaged"
    LOST = "lost"
    DECOMMISSIONED = "decommissioned"


class Book(BaseModel):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    edition: Mapped[str | None] = mapped_column(String(30), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)  # e.g. "Science", "Fiction"
    subject_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    shelf_location: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "Shelf A-3"
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)
    purchase_price: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    issues = relationship("LibraryIssue", back_populates="book")

    def __repr__(self) -> str:
        return f"<Book '{self.title}' ({self.available_copies}/{self.total_copies})>"


class LibraryIssue(BaseModel):
    """Records a book being issued to a student or teacher."""
    __tablename__ = "library_issues"

    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=True)
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.id"), nullable=True)

    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_returned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Fine details
    fine_per_day: Mapped[float] = mapped_column(Numeric(6, 2), default=0.50)
    fine_amount: Mapped[float] = mapped_column(Numeric(8, 2), default=0.0)
    fine_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    condition_on_issue: Mapped[str | None] = mapped_column(String(50), nullable=True)   # Good, Fair, Poor
    condition_on_return: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    issued_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    received_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    @property
    def days_overdue(self) -> int:
        from datetime import date as today_date
        if self.is_returned:
            return 0
        delta = today_date.today() - self.due_date
        return max(0, delta.days)

    @property
    def calculated_fine(self) -> float:
        return self.days_overdue * float(self.fine_per_day)

    book = relationship("Book", back_populates="issues")
    student = relationship("Student", back_populates="library_issues")
    teacher = relationship("Teacher", foreign_keys=[teacher_id])
    issuer = relationship("User", foreign_keys=[issued_by])
    receiver = relationship("User", foreign_keys=[received_by])

    def __repr__(self) -> str:
        return f"<LibraryIssue book={self.book_id} due={self.due_date}>"