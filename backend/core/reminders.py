"""F25 — Automated appointment reminders.

Runs via APScheduler every 30 minutes.
Finds appointments starting in ~24 hours (window: 23h30–24h30) that have not
had a reminder sent yet, then sends email + WhatsApp to the client.
"""

import logging
import os
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

REMINDER_HOURS_BEFORE = int(os.getenv("REMINDER_HOURS_BEFORE", "24"))
REMINDER_WINDOW_MINUTES = 30  # ±30 min around the target hour


def send_appointment_reminders(db: Session) -> int:
    """Query due reminders and send them. Returns the count sent."""
    from backend.core.appointment import Appointment
    from backend.core.barber import Barber
    from backend.core.client import Client
    from backend.core.notifications import AppointmentNotification, get_notification_service
    from backend.core.service import Service
    from backend.core.whatsapp import build_whatsapp_service

    now = datetime.now()
    window_start = now + timedelta(hours=REMINDER_HOURS_BEFORE) - timedelta(minutes=REMINDER_WINDOW_MINUTES)
    window_end = now + timedelta(hours=REMINDER_HOURS_BEFORE) + timedelta(minutes=REMINDER_WINDOW_MINUTES)

    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.deleted.is_(False),
            Appointment.start_at >= window_start,
            Appointment.start_at < window_end,
            Appointment.reminder_sent_at.is_(None),
        )
        .all()
    )

    sent = 0
    notif_service = get_notification_service()
    wa_service = build_whatsapp_service()

    for appt in appointments:
        try:
            client = db.query(Client).filter(Client.id == appt.client_id).first()
            barber = db.query(Barber).filter(Barber.id == appt.barber_id).first()
            service = db.query(Service).filter(Service.id == appt.service_id).first()

            if not (client and barber and service):
                continue

            notif = AppointmentNotification(
                client_name=client.nome,
                client_email=client.email,
                barber_name=barber.nome,
                service_name=service.nome,
                start_at=appt.start_at,
                appointment_id=appt.id,
            )

            # Email reminder
            notif_service.send_reminder(notif)

            # WhatsApp reminder to client (if phone available)
            if client.telefone:
                wa_service.notify_client_reminder(
                    client_phone=client.telefone,
                    client_name=client.nome,
                    barber_name=barber.nome,
                    service_name=service.nome,
                    start_at=appt.start_at,
                    appointment_id=appt.id,
                )

            appt.reminder_sent_at = now
            sent += 1

        except Exception:  # noqa: BLE001
            logger.exception("Failed to send reminder for appointment %s", appt.id)

    if sent:
        db.commit()

    logger.info("Reminders sent: %d", sent)
    return sent
