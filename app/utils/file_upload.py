"""
File upload utilities — handles image uploads for students and teachers.
"""
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings


def _ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


async def save_photo(file: UploadFile, subfolder: str = "photos") -> str:
    """
    Save an uploaded photo to the media directory.
    Returns the relative URL path.
    Raises HTTPException if file type or size is invalid.
    """
    # Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed: {settings.ALLOWED_IMAGE_TYPES}",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Generate unique filename preserving extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"

    save_dir = _ensure_dir(os.path.join(settings.MEDIA_ROOT, subfolder))
    file_path = save_dir / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    return f"/media/{subfolder}/{filename}"


def delete_file(relative_url: str) -> None:
    """Remove a previously uploaded file from disk."""
    if not relative_url:
        return
    path = Path(settings.MEDIA_ROOT) / relative_url.lstrip("/media/")
    if path.exists():
        path.unlink()