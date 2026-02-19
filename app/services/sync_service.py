"""
Sync service — handles pushing local data to cloud and receiving cloud data.
"""
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.sync import SyncStatus, build_sync_headers, check_internet_connection
from app.models import MODEL_MAP

logger = logging.getLogger(__name__)

# Tables synced in order (respect FK dependencies)
SYNC_ORDER = [
    "users", "classes", "subjects", "teachers", "teacher_subjects",
    "students", "timetable_slots",
    "student_attendance", "teacher_attendance",
    "fee_structures", "fee_invoices", "fee_invoice_items", "fee_payments",
    "exams", "exam_schedules", "exam_results",
    "books", "library_issues",
    "buses", "transport_routes", "transport_assignments",
    "inventory_items", "maintenance_records",
    "transfer_records", "suspension_records", "salary_records",
]


async def push_table(session: AsyncSession, table_name: str, client: httpx.AsyncClient) -> int:
    """Push unsynced records for a table to cloud. Returns count synced."""
    Model = MODEL_MAP.get(table_name)
    if not Model:
        return 0

    result = await session.execute(
        select(Model).where(
            Model.is_synced == False,
            Model.deleted_at.is_(None),
        ).limit(200)
    )
    records = result.scalars().all()
    if not records:
        return 0

    payload = [r.to_sync_dict() for r in records]

    try:
        response = await client.post(
            f"{settings.CLOUD_API_URL}/api/v1/sync/receive/{table_name}",
            json=payload,
            headers=build_sync_headers(),
            timeout=30.0,
        )
        response.raise_for_status()

        ids = [r.id for r in records]
        await session.execute(
            update(Model)
            .where(Model.id.in_(ids))
            .values(is_synced=True, synced_at=datetime.utcnow())
        )
        await session.commit()
        logger.info(f"[sync] Pushed {len(records)} records from '{table_name}'")
        return len(records)

    except httpx.HTTPStatusError as e:
        logger.error(f"[sync] HTTP error for '{table_name}': {e.response.status_code}")
        return 0
    except Exception as e:
        logger.error(f"[sync] Failed to push '{table_name}': {e}")
        return 0


async def push_deleted_records(session: AsyncSession, table_name: str, client: httpx.AsyncClient) -> int:
    """Notify cloud about soft-deleted records."""
    Model = MODEL_MAP.get(table_name)
    if not Model:
        return 0

    result = await session.execute(
        select(Model).where(
            Model.deleted_at.isnot(None),
            Model.is_synced == False,
        ).limit(100)
    )
    records = result.scalars().all()
    if not records:
        return 0

    ids = [str(r.id) for r in records]
    try:
        response = await client.request(
            "DELETE",
            f"{settings.CLOUD_API_URL}/api/v1/sync/delete/{table_name}",
            json={"ids": ids},
            headers=build_sync_headers(),
        )
        response.raise_for_status()

        await session.execute(
            update(Model)
            .where(Model.id.in_([r.id for r in records]))
            .values(is_synced=True, synced_at=datetime.utcnow())
        )
        await session.commit()
        return len(records)
    except Exception as e:
        logger.error(f"[sync] Failed to push deletions for '{table_name}': {e}")
        return 0


async def run_full_sync(session: AsyncSession) -> dict[str, Any]:
    """
    Main sync entry point. Checks internet, then pushes all unsynced data.
    Returns a summary dict.
    """
    if SyncStatus.is_running:
        return {"status": "skipped", "reason": "Sync already in progress"}

    if not await check_internet_connection():
        return {"status": "offline", "reason": "No internet connection"}

    SyncStatus.is_running = True
    SyncStatus.last_run = datetime.utcnow()

    summary = {"status": "ok", "tables": {}, "total": 0}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for table in SYNC_ORDER:
                pushed = await push_table(session, table, client)
                deleted = await push_deleted_records(session, table, client)
                if pushed or deleted:
                    summary["tables"][table] = {"pushed": pushed, "deleted": deleted}
                    summary["total"] += pushed + deleted

        SyncStatus.last_success = datetime.utcnow()
        SyncStatus.total_synced += summary["total"]
        SyncStatus.last_error = None

    except Exception as e:
        SyncStatus.last_error = str(e)
        summary["status"] = "error"
        summary["error"] = str(e)
        logger.error(f"[sync] Full sync failed: {e}")
    finally:
        SyncStatus.is_running = False

    logger.info(f"[sync] Complete — {summary['total']} records synced")
    return summary


async def receive_sync_data(session: AsyncSession, table_name: str, payload: list[dict]) -> int:
    """
    Cloud-side endpoint handler: upsert incoming records using last-write-wins.
    """
    Model = MODEL_MAP.get(table_name)
    if not Model:
        logger.warning(f"[sync/receive] Unknown table: {table_name}")
        return 0

    count = 0
    for record_data in payload:
        try:
            existing = await session.get(Model, UUID(record_data["id"]))

            if existing:
                incoming_ts = datetime.fromisoformat(record_data.get("updated_at", ""))
                if incoming_ts > existing.updated_at:
                    for k, v in record_data.items():
                        if k not in ("id", "created_at"):
                            try:
                                setattr(existing, k, v)
                            except Exception:
                                pass
                    existing.is_synced = True
            else:
                record_data["is_synced"] = True
                obj = Model(**record_data)
                session.add(obj)

            count += 1
        except Exception as e:
            logger.error(f"[sync/receive] Error processing record {record_data.get('id')}: {e}")

    await session.commit()
    return count