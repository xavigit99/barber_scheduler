import logging
import os

from sqlalchemy.orm import Session

from backend.core.barbershop import Barbershop

logger = logging.getLogger(__name__)

PLAN_BY_PRICE_ENV = {
    "STRIPE_PRICE_BASIC": "basic",
    "STRIPE_PRICE_PRO": "pro",
    "STRIPE_PRICE_PREMIUM": "premium",
}


def _resolve_plan_from_subscription(subscription: dict) -> str:
    metadata = subscription.get("metadata", {}) or {}
    if metadata.get("plan"):
        return metadata["plan"]

    price_id = None
    items = subscription.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id")

    for env_name, plan in PLAN_BY_PRICE_ENV.items():
        if os.getenv(env_name) == price_id:
            return plan
    return "free"


def handle_billing_webhook(db: Session, payload: bytes, sig_header: str) -> dict:
    import stripe

    stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not stripe_key or not webhook_secret:
        raise ValueError("Stripe webhook is not configured")

    stripe.api_key = stripe_key
    event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
      if data.get("mode") != "subscription":
          return {"status": "ignored"}
      barbershop_id = data.get("metadata", {}).get("barbershop_id")
      if barbershop_id:
          barbershop = db.query(Barbershop).filter(Barbershop.id == int(barbershop_id)).first()
          if barbershop:
              barbershop.stripe_customer_id = data.get("customer")
              barbershop.stripe_subscription_id = data.get("subscription")
              barbershop.billing_plan = data.get("metadata", {}).get("plan", "free")
              barbershop.subscription_status = "active"
              db.commit()

    if event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
        subscription = data
        customer_id = subscription.get("customer")
        if customer_id:
            barbershop = (
                db.query(Barbershop)
                .filter(Barbershop.stripe_customer_id == customer_id)
                .first()
            )
            if barbershop:
                status = subscription.get("status", "inactive")
                plan = _resolve_plan_from_subscription(subscription)
                barbershop.stripe_subscription_id = subscription.get("id")
                barbershop.subscription_status = status
                barbershop.billing_plan = plan if status != "canceled" else "free"
                if status == "canceled":
                    barbershop.stripe_subscription_id = None
                db.commit()
                logger.info("Updated subscription for barbershop %s", barbershop.id)

    return {"status": "ok"}
