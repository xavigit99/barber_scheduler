import io
import os

from fastapi import APIRouter, Response

router = APIRouter(prefix="/public", tags=["QR Code"])


@router.get("/qr/{tenant_id}")
async def generate_qr(tenant_id: int) -> Response:
    """Generates a QR code PNG pointing to the public booking page (F39)."""
    import qrcode

    base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")
    booking_url = f"{base_url}/book/{tenant_id}"

    img = qrcode.make(booking_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")
