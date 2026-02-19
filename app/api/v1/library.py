from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import Permission, require_permission
from app.database import get_db
from app.models.user import User
from app.models.library import Book, LibraryIssue
from app.schemas.library import BookCreate, BookUpdate, BookResponse, IssueBookRequest, ReturnBookRequest
from app.utils.pagination import paginate

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("/books")
async def list_books(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.LIBRARY_READ)),
):
    q = select(Book).where(Book.deleted_at.is_(None))
    if search:
        t = f"%{search}%"
        q = q.where(Book.title.ilike(t) | Book.author.ilike(t) | Book.isbn.ilike(t))
    if category:
        q = q.where(Book.category == category)
    count = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    r = await db.execute(q.offset(skip).limit(limit).order_by(Book.title))
    return paginate(r.scalars().all(), count, skip, limit)


@router.post("/books", status_code=201)
async def add_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.LIBRARY_WRITE)),
):
    book = Book(**data.model_dump(), available_copies=data.total_copies, is_synced=False)
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


@router.get("/books/{book_id}")
async def get_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.LIBRARY_READ)),
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book


@router.put("/books/{book_id}")
async def update_book(
    book_id: UUID,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.LIBRARY_WRITE)),
):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(book, f, v)
    book.is_synced = False
    await db.commit()
    await db.refresh(book)
    return book


@router.post("/issue", status_code=201)
async def issue_book(
    data: IssueBookRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LIBRARY_WRITE)),
):
    book = await db.get(Book, data.book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    if book.available_copies <= 0:
        raise HTTPException(400, "No copies available")
    issue = LibraryIssue(
        book_id=data.book_id,
        student_id=data.student_id,
        teacher_id=data.teacher_id,
        issue_date=date.today(),
        due_date=data.due_date,
        fine_per_day=data.fine_per_day,
        condition_on_issue=data.condition_on_issue,
        issued_by=current_user.id,
        is_synced=False,
    )
    db.add(issue)
    book.available_copies -= 1
    book.is_synced = False
    await db.commit()
    return {"message": "Book issued successfully", "issue_id": str(issue.id)}


@router.post("/return")
async def return_book(
    data: ReturnBookRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LIBRARY_WRITE)),
):
    issue = await db.get(LibraryIssue, data.issue_id)
    if not issue:
        raise HTTPException(404, "Issue record not found")
    if issue.is_returned:
        raise HTTPException(400, "Book already returned")
    issue.return_date = date.today()
    issue.is_returned = True
    issue.condition_on_return = data.condition_on_return
    issue.notes = data.notes
    issue.fine_amount = issue.calculated_fine
    issue.received_by = current_user.id
    issue.is_synced = False
    book = await db.get(Book, issue.book_id)
    if book:
        book.available_copies += 1
        book.is_synced = False
    await db.commit()
    return {
        "message": "Book returned successfully",
        "fine_amount": issue.fine_amount,
        "days_overdue": issue.days_overdue,
    }


@router.get("/fines")
async def outstanding_fines(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.LIBRARY_READ)),
):
    r = await db.execute(
        select(LibraryIssue)
        .where(LibraryIssue.is_returned == False, LibraryIssue.deleted_at.is_(None))
        .order_by(LibraryIssue.due_date)
    )
    return [i for i in r.scalars().all() if i.days_overdue > 0]


@router.get("/history/{student_id}")
async def student_library_history(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.LIBRARY_READ)),
):
    r = await db.execute(
        select(LibraryIssue)
        .where(LibraryIssue.student_id == student_id)
        .order_by(LibraryIssue.issue_date.desc())
    )
    return r.scalars().all()
