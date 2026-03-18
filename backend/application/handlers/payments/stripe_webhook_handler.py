import logging
import os

from sqlalchemy.orm import Session

from backend.core.appointment import Appointment

logger = logging.getLogger(__name__)


def handle_stripe_webhook(db: Session, payload: bytes, sig_header: str) -> dict:
    """Process a Stripe webhook event.

    This is NOT a diator handler because it receives raw bytes (not a frozen dataclass).
    It is called directly from the route.
    """
    import stripe

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET not configured")

    event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        appointment_id = session.get("metadata", {}).get("appointment_id")
        if appointment_id:
            appointment = (
                db.query(Appointment)
                .filter(
                    Appointment.id == int(appointment_id),
                    Appointment.deleted.is_(False),
                )
                .first()
            )
            if appointment:
                appointment.payment_status = "paid"
                db.commit()
                logger.info("Payment completed for appointment %s", appointment_id)
            else:
                logger.warning("Appointment %s not found for payment", appointment_id)

    return {"status": "ok"}
