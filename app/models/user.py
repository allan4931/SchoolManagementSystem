"""
User model — system accounts with role-based access control.
"""
import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HEADMASTER = "headmaster"
    TEACHER = "teacher"
    BURSAR = "bursar"
    CLERK = "clerk"


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.CLERK,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    profile_photo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Refresh token (stored hashed for security)
    refresh_token_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships (back-references from other models)
    fee_payments_received = relationship("FeePayment", back_populates="received_by_user", foreign_keys="FeePayment.received_by")

    def __repr__(self) -> str:
        return f"<User {self.username} [{self.role}]>"