"""
Model registry — imports all models so SQLAlchemy knows about them.
Also provides MODEL_MAP for the sync worker.
"""
from app.models.user import User
from app.models.student import Student, TransferRecord, SuspensionRecord
from app.models.teacher import Teacher, SalaryRecord
from app.models.class_ import Class, TimetableSlot
from app.models.subject import Subject, TeacherSubject
from app.models.attendance import StudentAttendance, TeacherAttendance
from app.models.fee import FeeStructure, FeeInvoice, FeeInvoiceItem, FeePayment
from app.models.exam import Exam, ExamSchedule, ExamResult
from app.models.library import Book, LibraryIssue
from app.models.transport import Bus, TransportRoute, TransportAssignment
from app.models.inventory import InventoryItem, MaintenanceRecord

# Registry used by the sync worker to map table names → Model classes
MODEL_MAP = {
    "users": User,
    "students": Student,
    "transfer_records": TransferRecord,
    "suspension_records": SuspensionRecord,
    "teachers": Teacher,
    "salary_records": SalaryRecord,
    "classes": Class,
    "timetable_slots": TimetableSlot,
    "subjects": Subject,
    "teacher_subjects": TeacherSubject,
    "student_attendance": StudentAttendance,
    "teacher_attendance": TeacherAttendance,
    "fee_structures": FeeStructure,
    "fee_invoices": FeeInvoice,
    "fee_invoice_items": FeeInvoiceItem,
    "fee_payments": FeePayment,
    "exams": Exam,
    "exam_schedules": ExamSchedule,
    "exam_results": ExamResult,
    "books": Book,
    "library_issues": LibraryIssue,
    "buses": Bus,
    "transport_routes": TransportRoute,
    "transport_assignments": TransportAssignment,
    "inventory_items": InventoryItem,
    "maintenance_records": MaintenanceRecord,
}

__all__ = [
    "User", "Student", "TransferRecord", "SuspensionRecord",
    "Teacher", "SalaryRecord", "Class", "TimetableSlot",
    "Subject", "TeacherSubject", "StudentAttendance", "TeacherAttendance",
    "FeeStructure", "FeeInvoice", "FeeInvoiceItem", "FeePayment",
    "Exam", "ExamSchedule", "ExamResult", "Book", "LibraryIssue",
    "Bus", "TransportRoute", "TransportAssignment",
    "InventoryItem", "MaintenanceRecord", "MODEL_MAP",
]