from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.update_appointment_payment_command import (
    UpdateAppointmentPaymentCommand,
)
from backend.core.appointment import Appointment
from backend.core.exceptions import NotFoundError, ValidationError
from repositories.base_repository import BaseRepository

LOCAL_PAYMENT_METHODS = {
    "cash",
    "mbway",
    "multibanco",
    "card_terminal",
    "bank_transfer",
}

PAYMENT_STATUSES = {
    "not_required",
    "pending",
    "paid",
    "refunded",
}


class UpdateAppointmentPaymentHandler(
    RequestHandler[UpdateAppointmentPaymentCommand, object]
):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: UpdateAppointmentPaymentCommand):
        if command.payment_status not in PAYMENT_STATUSES:
            raise ValidationError("Invalid payment status")

        if (
            command.payment_method is not None
            and command.payment_method not in LOCAL_PAYMENT_METHODS
        ):
            raise ValidationError("Invalid payment method")

        if command.payment_status == "not_required":
            payment_method = None
        else:
            payment_method = command.payment_method
            if payment_method is None:
                raise ValidationError("Payment method is required for this payment status")

        repository = BaseRepository(
            Appointment,
            self.db,
            tenant_id=command.tenant_id,
        )
        appointment = repository.get(command.appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")

        appointment.payment_status = command.payment_status
        appointment.payment_method = payment_method
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
