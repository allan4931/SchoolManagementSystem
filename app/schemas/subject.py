from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SubjectCreate(BaseModel):
    name: str
    code: str
    department: Optional[str] = None
    is_elective: bool = False
    max_marks: float = 100.0
    pass_mark: float = 50.0
    description: Optional[str] = None
    credit_hours: int = 1


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    is_elective: Optional[bool] = None
    max_marks: Optional[float] = None
    pass_mark: Optional[float] = None


class SubjectResponse(BaseModel):
    id: UUID
    name: str
    code: str
    department: Optional[str]
    is_elective: bool
    max_marks: float
    pass_mark: float
    credit_hours: int
    created_at: datetime

    class Config:
        from_attributes = True
