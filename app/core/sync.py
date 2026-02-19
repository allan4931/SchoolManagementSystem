"""
Sync utilities: internet detection, sync status tracking.
"""
import httpx
import logging
from datetime import datetime
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


async def check_internet_connection() -> bool:
    """
    Check if the internet is reachable by pinging the cloud server.
    Returns True if connected, False otherwise.
    """
    if not settings.CLOUD_PING_URL or not settings.ENABLE_SYNC:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.CLOUD_PING_URL)
            return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
        return False
    except Exception as e:
        logger.warning(f"Internet check failed unexpectedly: {e}")
        return False


def build_sync_headers() -> dict[str, str]:
    """Build the auth headers required by the cloud sync endpoint."""
    return {
        "X-Sync-Token": settings.SYNC_SECRET_TOKEN or "",
        "Content-Type": "application/json",
        "X-Source": "lan-server",
    }


class SyncStatus:
    """In-memory tracker for the most recent sync run."""
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    total_synced: int = 0
    is_running: bool = False

    @classmethod
    def to_dict(cls) -> dict:
        return {
            "last_run": cls.last_run.isoformat() if cls.last_run else None,
            "last_success": cls.last_success.isoformat() if cls.last_success else None,
            "last_error": cls.last_error,
            "total_records_synced": cls.total_synced,
            "is_running": cls.is_running,
            "sync_enabled": settings.ENABLE_SYNC,
            "sync_interval_minutes": settings.SYNC_INTERVAL_MINUTES,
        }