"""
Base SQLAlchemy model shared by all tables.
Includes audit fields and sync tracking fields.
"""
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Boolean, DateTime, String, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BaseModel(Base):
    """
    Abstract base model providing:
      - UUID primary key
      - Audit timestamps (created_at, updated_at)
      - Soft delete support (deleted_at)
      - Sync tracking (is_synced, synced_at, local_id)
    """
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )
    is_synced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    # Stores the temporary client-side ID before UUID assignment
    local_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted without removing from DB."""
        self.deleted_at = datetime.utcnow()
        self.is_synced = False  # needs to sync the deletion

    def mark_synced(self) -> None:
        """Mark record as successfully synced to cloud."""
        self.is_synced = True
        self.synced_at = datetime.utcnow()

    def to_sync_dict(self) -> Dict[str, Any]:
        """Serialize record for cloud sync payload."""
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                result[col.name] = val.isoformat()
            elif isinstance(val, uuid.UUID):
                result[col.name] = str(val)
            else:
                result[col.name] = val
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"