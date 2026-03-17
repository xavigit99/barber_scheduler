from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.cancel_appointment_command import CancelAppointmentCommand
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.client import Client
from backend.core.service import Service


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
        appointment.deleted_at = datetime.now(UTC)
        self.db.commit()

        # Best-effort cancellation notification
        from backend.core.notifications import AppointmentNotification, get_notification_service

        try:
            client = self.db.query(Client).filter(Client.id == appointment.client_id).first()
            barber = self.db.query(Barber).filter(Barber.id == appointment.barber_id).first()
            service = self.db.query(Service).filter(Service.id == appointment.service_id).first()
            get_notification_service().send_cancellation(
                AppointmentNotification(
                    client_name=client.nome if client else "",
                    client_email=client.email if client else "",
                    barber_name=barber.nome if barber else "",
                    service_name=service.nome if service else "",
                    start_at=appointment.start_at,
                    appointment_id=appointment.id,
                )
            )
        except Exception:  # noqa: BLE001
            pass

        return True
