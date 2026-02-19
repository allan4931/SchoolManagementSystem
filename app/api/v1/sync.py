"""
Sync endpoints: manual trigger, status check, and cloud receive (cloud-side).
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.permissions import require_roles
from app.core.sync import SyncStatus
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.services.sync_service import run_full_sync, receive_sync_data

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("/status")
async def sync_status(_: User = Depends(get_current_user)):
    """Return the current sync status and last run info."""
    return SyncStatus.to_dict()


@router.post("/trigger")
async def trigger_sync(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    """Manually trigger a cloud sync (admin only)."""
    if not settings.ENABLE_SYNC:
        raise HTTPException(400, "Cloud sync is disabled on this server")
    result = await run_full_sync(db)
    return result


# ── Cloud-side endpoints (used by LAN servers to push data) ──────────────────

async def verify_sync_token(x_sync_token: str = Header(...)):
    """Dependency: validate the sync secret token."""
    if not settings.SYNC_SECRET_TOKEN:
        raise HTTPException(503, "Sync not configured on this server")
    if x_sync_token != settings.SYNC_SECRET_TOKEN:
        raise HTTPException(401, "Invalid sync token")


@router.post("/receive/{table_name}")
async def receive_data(
    table_name: str,
    payload: list[dict],
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_sync_token),
):
    """Cloud endpoint: receive pushed records from a LAN server."""
    count = await receive_sync_data(db, table_name, payload)
    return {"status": "ok", "table": table_name, "records_processed": count}


@router.delete("/delete/{table_name}")
async def receive_deletions(
    table_name: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_sync_token),
):
    """Cloud endpoint: receive deletion notifications from a LAN server."""
    from app.models import MODEL_MAP
    from uuid import UUID

    Model = MODEL_MAP.get(table_name)
    if not Model:
        raise HTTPException(400, f"Unknown table: {table_name}")

    ids = body.get("ids", [])
    for id_str in ids:
        obj = await db.get(Model, UUID(id_str))
        if obj and not obj.is_deleted:
            obj.soft_delete()

    await db.commit()
    return {"status": "ok", "deleted": len(ids)}


@router.get("/health")
async def health():
    """Simple health check endpoint for internet detection."""
    return {"status": "online", "service": settings.APP_NAME}