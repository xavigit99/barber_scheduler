"""F31 — Automated birthday messages.

APScheduler job that runs daily at 09:00.
Finds clients with birthday today (same day + month) that haven't received a
message this year, then sends email + WhatsApp.
"""

import logging
from datetime import date

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def send_birthday_messages(db: Session) -> int:
    """Send birthday messages to eligible clients. Returns count sent."""
    from backend.core.client import Client
    from backend.core.notifications import get_notification_service
    from backend.core.whatsapp import build_whatsapp_service

    today = date.today()
    current_year = today.year

    clients = (
        db.query(Client)
        .filter(
            Client.deleted.is_(False),
            Client.data_nascimento.isnot(None),
        )
        .all()
    )

    # Filter in Python — extract day/month from date
    due = [
        c for c in clients
        if c.data_nascimento.day == today.day
        and c.data_nascimento.month == today.month
        and c.birthday_msg_year != current_year
    ]

    notif_service = get_notification_service()
    wa_service = build_whatsapp_service()
    sent = 0

    for client in due:
        try:
            # Email
            notif_service.send_birthday(client_name=client.nome, client_email=client.email)

            # WhatsApp
            if client.telefone:
                wa_service.notify_client_birthday(
                    client_phone=client.telefone,
                    client_name=client.nome,
                )

            client.birthday_msg_year = current_year
            sent += 1

        except Exception:  # noqa: BLE001
            logger.exception("Failed to send birthday message to client %s", client.id)

    if sent:
        db.commit()

    logger.info("Birthday messages sent: %d", sent)
    return sent
