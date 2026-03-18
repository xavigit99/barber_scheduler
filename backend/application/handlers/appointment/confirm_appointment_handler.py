from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.confirm_appointment_command import ConfirmAppointmentCommand
from backend.core.appointment import Appointment
from backend.core.exceptions import NotFoundError


class ConfirmAppointmentHandler(RequestHandler[ConfirmAppointmentCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: ConfirmAppointmentCommand):
        appointment = (
            self.db.query(Appointment)
            .filter(
                Appointment.confirmation_token == command.token,
                Appointment.deleted.is_(False),
            )
            .first()
        )
        if appointment is None:
            raise NotFoundError("Invalid or expired confirmation link")

        if appointment.status != "confirmed":
            appointment.status = "confirmed"
            appointment.confirmed_at = datetime.now()
            appointment.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(appointment)

        return appointment
