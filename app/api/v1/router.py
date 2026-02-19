from fastapi import APIRouter
from app.api.v1 import (
    auth,
    students,
    teachers,
    classes,
    subjects,
    attendance,
    fees,
    exams,
    library,
    transport,
    inventory,
    sync,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(teachers.router)
api_router.include_router(classes.router)
api_router.include_router(subjects.router)
api_router.include_router(attendance.router)
api_router.include_router(fees.router)
api_router.include_router(exams.router)
api_router.include_router(library.router)
api_router.include_router(transport.router)
api_router.include_router(inventory.router)
api_router.include_router(sync.router)
