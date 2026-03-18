import os

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_checkout_command import CreateCheckoutCommand
from backend.core.appointment import Appointment
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class CreateCheckoutHandler(RequestHandler[CreateCheckoutCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateCheckoutCommand) -> dict:
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe_key:
            raise ValidationError("Stripe is not configured (STRIPE_SECRET_KEY missing)")

        repo = BaseRepository(Appointment, self.db, tenant_id=command.tenant_id)
        appointment = repo.get(command.appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")

        service = (
            self.db.query(Service)
            .filter(Service.id == appointment.service_id, Service.deleted.is_(False))
            .first()
        )
        if service is None:
            raise NotFoundError("Service not found")

        import stripe

        stripe.api_key = stripe_key

        base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": service.nome},
                        "unit_amount": int(service.preco * 100),
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{base_url}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/payments/cancel",
            metadata={"appointment_id": str(appointment.id)},
        )

        appointment.payment_status = "pending"
        self.db.commit()

        return {"checkout_url": session.url}
