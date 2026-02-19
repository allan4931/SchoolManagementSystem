"""
Pagination utilities for list endpoints.
"""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    pages: int
    items: List[T]


def paginate(items: list, total: int, skip: int, limit: int) -> dict:
    """Build a standardized paginated response dict."""
    page = (skip // limit) + 1 if limit else 1
    pages = (total + limit - 1) // limit if limit else 1
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "items": items,
    }