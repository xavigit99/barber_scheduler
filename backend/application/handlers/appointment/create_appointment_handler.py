from datetime import UTC, datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_appointment_command import CreateAppointmentCommand
from backend.core.appointment import Appointment
from backend.core.appointment_utils import (
    ensure_not_blocked,
    ensure_within_availability_windows,
)
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.barber_block import BarberBlock
from backend.core.client import Client
from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.scheduling import ensure_valid_timezone, normalize_local_datetime
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class CreateAppointmentHandler(RequestHandler[CreateAppointmentCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateAppointmentCommand):
        tenant_id = command.tenant_id
        barber_repository = BaseRepository(Barber, self.db, tenant_id)
        client_repository = BaseRepository(Client, self.db, tenant_id)
        service_repository = BaseRepository(Service, self.db, tenant_id)

        barber = barber_repository.get(command.barber_id)
        if barber is None:
            raise NotFoundError("Barber not found")

        client = client_repository.get(command.client_id)
        if client is None:
            raise NotFoundError("Client not found")

        service = service_repository.get(command.service_id)
        if service is None:
            raise NotFoundError("Service not found")

        # Normalize start_at to local timezone (Europe/Lisbon) for availability check
        # Database availability (Time) is stored as local time
        timezone = ensure_valid_timezone("Europe/Lisbon")
        start_at = normalize_local_datetime(command.start_at, timezone)
        end_at = start_at + timedelta(minutes=service.duracao_minutos)

        availability_windows = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == command.barber_id,
                BarberAvailability.deleted.is_(False),
            )
            .all()
        )
        ensure_within_availability_windows(availability_windows, start_at, end_at)

        blocks = (
            self.db.query(BarberBlock)
            .filter(
                BarberBlock.barber_id == command.barber_id,
                BarberBlock.deleted.is_(False),
            )
            .all()
        )
        ensure_not_blocked(blocks, start_at, end_at)

        overlapping = (
            self.db.query(Appointment)
            .filter(
                Appointment.barber_id == command.barber_id,
                Appointment.deleted.is_(False),
                Appointment.start_at < end_at,
                Appointment.end_at > start_at,
            )
            .first()
        )
        if overlapping:
            raise ConflictError("Appointment overlaps an existing booking")

        now = datetime.now()
        appointment = Appointment(
            barber_id=command.barber_id,
            client_id=command.client_id,
            service_id=command.service_id,
            tenant_id=tenant_id,
            start_at=start_at,
            end_at=end_at,
            created_at=now,
            updated_at=now,
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)

        # Notify client (best-effort — never fail the main operation)
        try:
            from backend.core.notifications import AppointmentNotification, get_notification_service

            get_notification_service().send_confirmation(
                AppointmentNotification(
                    client_name=client.nome,
                    client_email=client.email,
                    barber_name=barber.nome,
                    service_name=service.nome,
                    start_at=command.start_at,
                    appointment_id=appointment.id,
                )
            )
        except Exception:
            pass

        return appointment
