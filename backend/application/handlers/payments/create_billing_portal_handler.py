import os

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_billing_portal_command import (
    CreateBillingPortalCommand,
)
from backend.core.barbershop import Barbershop
from backend.core.exceptions import ForbiddenError, NotFoundError, ValidationError


class CreateBillingPortalHandler(RequestHandler[CreateBillingPortalCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateBillingPortalCommand) -> dict:
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe_key:
            raise ValidationError("Stripe is not configured")

        barbershop = (
            self.db.query(Barbershop)
            .filter(Barbershop.id == command.barbershop_id, Barbershop.deleted.is_(False))
            .first()
        )
        if barbershop is None:
            raise NotFoundError("Barbershop not found")
        if barbershop.owner_user_id != command.owner_user_id:
            raise ForbiddenError("Only the barbershop owner can manage billing")
        if not barbershop.stripe_customer_id:
            raise ValidationError("Barbershop has no Stripe customer yet")

        import stripe

        stripe.api_key = stripe_key
        app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5173").rstrip("/")
        session = stripe.billing_portal.Session.create(
            customer=barbershop.stripe_customer_id,
            return_url=f"{app_base_url}/admin/barbershops",
        )
        return {"portal_url": session.url}
