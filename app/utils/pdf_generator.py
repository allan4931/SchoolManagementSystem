"""
PDF response helper — wraps PDF bytes into a FastAPI streaming response.
"""
from fastapi.responses import StreamingResponse
import io


def pdf_response(pdf_bytes: bytes, filename: str = "document.pdf") -> StreamingResponse:
    """
    Wrap raw PDF bytes in a StreamingResponse for download.
    """
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )