"""
Role-Based Access Control (RBAC) system.
Defines what each role can do and provides FastAPI dependency injectors.
"""
from functools import wraps
from typing import List

from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User, UserRole


# ── Permission Constants ──────────────────────────────────────────────────────
class Permission:
    # Student permissions
    STUDENT_READ = "students:read"
    STUDENT_WRITE = "students:write"
    STUDENT_DELETE = "students:delete"

    # Teacher permissions
    TEACHER_READ = "teachers:read"
    TEACHER_WRITE = "teachers:write"
    TEACHER_DELETE = "teachers:delete"

    # Class permissions
    CLASS_READ = "classes:read"
    CLASS_WRITE = "classes:write"

    # Attendance permissions
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_WRITE = "attendance:write"

    # Fee permissions
    FEE_READ = "fees:read"
    FEE_WRITE = "fees:write"
    FEE_DELETE = "fees:delete"

    # Exam permissions
    EXAM_READ = "exams:read"
    EXAM_WRITE = "exams:write"
    MARKS_WRITE = "marks:write"

    # Library permissions
    LIBRARY_READ = "library:read"
    LIBRARY_WRITE = "library:write"

    # Transport permissions
    TRANSPORT_READ = "transport:read"
    TRANSPORT_WRITE = "transport:write"

    # Inventory permissions
    INVENTORY_READ = "inventory:read"
    INVENTORY_WRITE = "inventory:write"

    # Reports
    REPORTS_READ = "reports:read"

    # Admin only
    ADMIN_PANEL = "admin:panel"
    USER_MANAGE = "users:manage"
    SYNC_MANAGE = "sync:manage"


# ── Role Permission Map ───────────────────────────────────────────────────────
ROLE_PERMISSIONS: dict[str, list[str]] = {
    UserRole.ADMIN: ["*"],  # Full access to everything

    UserRole.HEADMASTER: [
        Permission.STUDENT_READ, Permission.STUDENT_WRITE,
        Permission.TEACHER_READ, Permission.TEACHER_WRITE,
        Permission.CLASS_READ, Permission.CLASS_WRITE,
        Permission.ATTENDANCE_READ,
        Permission.FEE_READ,
        Permission.EXAM_READ, Permission.EXAM_WRITE,
        Permission.LIBRARY_READ,
        Permission.TRANSPORT_READ,
        Permission.INVENTORY_READ,
        Permission.REPORTS_READ,
    ],

    UserRole.TEACHER: [
        Permission.STUDENT_READ,
        Permission.CLASS_READ,
        Permission.ATTENDANCE_READ, Permission.ATTENDANCE_WRITE,
        Permission.EXAM_READ, Permission.MARKS_WRITE,
        Permission.LIBRARY_READ, Permission.LIBRARY_WRITE,
    ],

    UserRole.BURSAR: [
        Permission.STUDENT_READ,
        Permission.FEE_READ, Permission.FEE_WRITE, Permission.FEE_DELETE,
        Permission.REPORTS_READ,
        Permission.TRANSPORT_READ, Permission.TRANSPORT_WRITE,
    ],

    UserRole.CLERK: [
        Permission.STUDENT_READ, Permission.STUDENT_WRITE,
        Permission.TEACHER_READ,
        Permission.CLASS_READ,
        Permission.ATTENDANCE_READ, Permission.ATTENDANCE_WRITE,
        Permission.LIBRARY_READ, Permission.LIBRARY_WRITE,
        Permission.INVENTORY_READ,
    ],
}


def has_permission(user: User, permission: str) -> bool:
    """Check if a user's role has a given permission."""
    role_perms = ROLE_PERMISSIONS.get(user.role, [])
    return "*" in role_perms or permission in role_perms


def require_permission(permission: str):
    """
    FastAPI dependency factory.
    Usage: Depends(require_permission("students:write"))
    """
    async def _check(current_user: User = Depends(get_current_user)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: requires '{permission}'",
            )
        return current_user
    return _check


def require_any_permission(*permissions: str):
    """Allow access if user has ANY of the listed permissions."""
    async def _check(current_user: User = Depends(get_current_user)):
        for perm in permissions:
            if has_permission(current_user, perm):
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: requires one of {permissions}",
        )
    return _check


def require_roles(*roles: UserRole):
    """Restrict access to specific roles only."""
    async def _check(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return _check