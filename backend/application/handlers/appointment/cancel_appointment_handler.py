from sqlalchemy.orm import Session

from backend.application.commands.cancel_appointment_command import CancelAppointmentCommand
from backend.core.appointment import Appointment
from backend.core.exceptions import NotFoundError
from diator.requests import RequestHandler


class CancelAppointmentHandler(RequestHandler[CancelAppointmentCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CancelAppointmentCommand) -> bool:
        appointment = (
            self.db.query(Appointment)
            .filter(
                Appointment.id == command.appointment_id,
                Appointment.deleted.is_(False),
            )
            .first()
        )
        if appointment is None:
            return False

        appointment.deleted = True
        self.db.commit()
        return True
