import hashlib
import hmac
import json
import threading
import urllib.request

from sqlalchemy.orm import Session

from backend.core.webhook import Webhook


def dispatch_webhook_event(db: Session, tenant_id: int, event: str, payload: dict) -> None:
    """Fire webhooks non-blocking. Never raises."""
    try:
        webhooks = db.query(Webhook).filter(
            Webhook.tenant_id == tenant_id,
            Webhook.deleted.is_(False),
        ).all()
        subscribed = [w for w in webhooks if event in (w.events or [])]
        if not subscribed:
            return
        body = json.dumps(payload).encode()
        for wh in subscribed:
            sig = hmac.new(wh.secret.encode(), body, hashlib.sha256).hexdigest()
            threading.Thread(target=_post, args=(wh.url, body, sig), daemon=True).start()
    except Exception:  # noqa: BLE001
        pass


def _post(url: str, body: bytes, sig: str) -> None:
    try:
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json", "X-Barber-Signature": f"sha256={sig}"},
        )
        urllib.request.urlopen(req, timeout=5)  # noqa: S310
    except Exception:  # noqa: BLE001
        pass
