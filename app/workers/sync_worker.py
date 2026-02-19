"""
Background sync worker using APScheduler.
Runs on a configurable interval, detects internet, and pushes unsynced data to cloud.
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.sync_service import run_full_sync

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


async def sync_job() -> None:
    """The actual job function executed by APScheduler."""
    logger.info("[sync_worker] Starting scheduled sync job...")
    async with AsyncSessionLocal() as session:
        result = await run_full_sync(session)
    status = result.get("status", "unknown")
    total = result.get("total", 0)
    if status == "ok":
        logger.info(f"[sync_worker] Sync completed. Records synced: {total}")
    elif status == "offline":
        logger.info("[sync_worker] Skipped — no internet connection")
    elif status == "skipped":
        logger.info("[sync_worker] Skipped — another sync is running")
    else:
        logger.error(f"[sync_worker] Sync failed: {result.get('error', 'unknown error')}")


def start_sync_scheduler() -> None:
    """Register and start the sync scheduler. Called at app startup."""
    if not settings.ENABLE_SYNC:
        logger.info("[sync_worker] Cloud sync is disabled (ENABLE_SYNC=False)")
        return

    scheduler.add_job(
        sync_job,
        trigger=IntervalTrigger(minutes=settings.SYNC_INTERVAL_MINUTES),
        id="cloud_sync",
        name="Cloud Sync Job",
        replace_existing=True,
        max_instances=1,          # Prevent overlapping runs
        coalesce=True,            # Only run once if multiple triggers fire
    )
    scheduler.start()
    logger.info(
        f"[sync_worker] Scheduler started — syncing every {settings.SYNC_INTERVAL_MINUTES} minutes"
    )


def stop_sync_scheduler() -> None:
    """Gracefully shut down the scheduler on app shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[sync_worker] Scheduler stopped")