"""
Database configuration: async engine, session factory, and base model.
Uses SQLAlchemy 2.0 async style.
"""

import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# ── Declarative Base ─────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Async Engine ─────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,         # must be async URL with +asyncpg
    echo=settings.DEBUG,           # log SQL in debug mode
    pool_pre_ping=True,
)

# ── Session Factory ───────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ── Dependency Injection ──────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: provides a DB session per request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ── Database Lifecycle ────────────────────────────────────────
async def init_db() -> None:
    """Create all tables on startup (dev only)."""
    async with engine.begin() as conn:
        # Import all models so Base knows about them
        from app.models import (
            user, student, teacher, class_, subject,
            attendance, fee, exam, library, transport, inventory
        )
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose engine connection pool on shutdown."""
    await engine.dispose()
