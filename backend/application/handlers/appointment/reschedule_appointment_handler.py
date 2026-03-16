from datetime import datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.reschedule_appointment_command import (
    RescheduleAppointmentCommand,
)
from backend.core.appointment import Appointment
from backend.core.appointment_utils import (
    ensure_not_blocked,
    ensure_within_availability_windows,
)
from backend.core.barber_availability import BarberAvailability
from backend.core.barber_block import BarberBlock
from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.service import Service


class RescheduleAppointmentHandler(RequestHandler[RescheduleAppointmentCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: RescheduleAppointmentCommand):
        appointment = (
            self.db.query(Appointment)
            .filter(
                Appointment.id == command.appointment_id,
                Appointment.deleted.is_(False),
            )
            .first()
        )
        if appointment is None:
            raise NotFoundError("Appointment not found")

        service = self.db.query(Service).filter(Service.id == appointment.service_id).first()
        if service is None:
            raise NotFoundError("Service not found")

        start_at = command.start_at
        end_at = start_at + timedelta(minutes=service.duracao_minutos)

        availability_windows = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == appointment.barber_id,
                BarberAvailability.deleted.is_(False),
            )
            .all()
        )
        ensure_within_availability_windows(availability_windows, start_at, end_at)

        blocks = (
            self.db.query(BarberBlock)
            .filter(
                BarberBlock.barber_id == appointment.barber_id,
                BarberBlock.deleted.is_(False),
            )
            .all()
        )
        ensure_not_blocked(blocks, start_at, end_at)

        overlapping = (
            self.db.query(Appointment)
            .filter(
                Appointment.barber_id == appointment.barber_id,
                Appointment.deleted.is_(False),
                Appointment.id != appointment.id,
                Appointment.start_at < end_at,
                Appointment.end_at > start_at,
            )
            .first()
        )
        if overlapping:
            raise ConflictError("Appointment overlaps an existing booking")

        appointment.start_at = start_at
        appointment.end_at = end_at
        appointment.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(appointment)

        # Best-effort reschedule notification
        from backend.core.notifications import AppointmentNotification, get_notification_service

        try:
            from backend.core.barber import Barber
            from backend.core.client import Client

            client = self.db.query(Client).filter(Client.id == appointment.client_id).first()
            barber = self.db.query(Barber).filter(Barber.id == appointment.barber_id).first()
            get_notification_service().send_reschedule(
                AppointmentNotification(
                    client_name=client.nome if client else "",
                    client_email=client.email if client else "",
                    barber_name=barber.nome if barber else "",
                    service_name=service.nome if service else "",
                    start_at=start_at,
                    appointment_id=appointment.id,
                )
            )
        except Exception:  # noqa: BLE001
            pass

        return appointment
