import os

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_subscription_checkout_command import (
    CreateSubscriptionCheckoutCommand,
)
from backend.core.barbershop import Barbershop
from backend.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from backend.core.user import User


def _price_id_for_plan(plan: str) -> str:
    env_name = f"STRIPE_PRICE_{plan.upper()}"
    price_id = os.getenv(env_name)
    if not price_id:
        raise ValidationError(f"{env_name} is not configured")
    return price_id


class CreateSubscriptionCheckoutHandler(
    RequestHandler[CreateSubscriptionCheckoutCommand, object]
):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateSubscriptionCheckoutCommand) -> dict:
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

        owner = self.db.query(User).filter(User.id == command.owner_user_id).first()
        if owner is None:
            raise NotFoundError("Owner user not found")

        import stripe

        stripe.api_key = stripe_key
        app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5173").rstrip("/")
        price_id = _price_id_for_plan(command.plan)

        customer_id = barbershop.stripe_customer_id
        if not customer_id:
            customer = stripe.Customer.create(
                email=owner.email,
                name=barbershop.nome,
                metadata={
                    "barbershop_id": str(barbershop.id),
                    "tenant_id": str(barbershop.tenant_id),
                    "owner_user_id": str(owner.id),
                },
            )
            customer_id = customer.id
            barbershop.stripe_customer_id = customer_id
            self.db.commit()

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{app_base_url}/admin/barbershops?billing=success",
            cancel_url=f"{app_base_url}/admin/barbershops?billing=cancel",
            metadata={
                "barbershop_id": str(barbershop.id),
                "plan": command.plan,
            },
            subscription_data={
                "metadata": {
                    "barbershop_id": str(barbershop.id),
                    "plan": command.plan,
                }
            },
        )
        return {"checkout_url": session.url}
