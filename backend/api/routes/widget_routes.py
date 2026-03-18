import os

from fastapi import APIRouter, Response

router = APIRouter(prefix="/public", tags=["Widget"])


@router.get("/widget/{tenant_id}")
async def embed_widget(tenant_id: int) -> Response:
    """Returns a JavaScript snippet that embeds a booking iframe (F40)."""
    base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")
    booking_url = f"{base_url}/book/{tenant_id}"

    js = (
        "(function(){"
        "var iframe = document.createElement('iframe');"
        f"iframe.src = '{booking_url}';"
        "iframe.width = '100%';"
        "iframe.height = '600px';"
        "iframe.frameBorder = '0';"
        "document.currentScript.parentNode.insertBefore(iframe, document.currentScript);"
        "})();"
    )

    return Response(content=js, media_type="application/javascript")
