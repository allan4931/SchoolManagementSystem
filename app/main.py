"""
School Management System — FastAPI Application Entry Point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import settings
from app.database import close_db, init_db
from app.workers.sync_worker import start_sync_scheduler, stop_sync_scheduler

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create media directory
    import os
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(f"{settings.MEDIA_ROOT}/students", exist_ok=True)
    os.makedirs(f"{settings.MEDIA_ROOT}/teachers", exist_ok=True)

    # NOTE: In production use Alembic migrations instead
    if settings.DEBUG:
        await init_db()
        logger.info("Database tables verified")

    # Start background sync scheduler
    start_sync_scheduler()
    logger.info("✅ Application ready")

    yield  # ← app runs here

    # Shutdown
    stop_sync_scheduler()
    await close_db()
    logger.info("👋 Application shutdown complete")


# ── App Factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready School Management System with LAN + Cloud Sync",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not settings.DEBUG:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)


# ── Global Exception Handlers ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."},
    )


# ── Static Files (media uploads) ──────────────────────────────────────────────
app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

# ── API Router ────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "school": settings.SCHOOL_NAME,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


# ── Dev server entry ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )