from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.application.commands.create_appointment_command import CreateAppointmentCommand
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.barber_block import BarberBlock
from backend.core.client import Client
from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.service import Service
from backend.core.appointment_utils import (
    ensure_not_blocked,
    ensure_within_availability_windows,
)
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class CreateAppointmentHandler(RequestHandler[CreateAppointmentCommand, object]):

    def __init__(self, db: Session):
        self.db = db
        self.barber_repository = BaseRepository(Barber, db)
        self.client_repository = BaseRepository(Client, db)
        self.service_repository = BaseRepository(Service, db)

    async def handle(self, command: CreateAppointmentCommand):
        barber = self.barber_repository.get(command.barber_id)
        if barber is None:
            raise NotFoundError("Barber not found")

        client = self.client_repository.get(command.client_id)
        if client is None:
            raise NotFoundError("Client not found")

        service = self.service_repository.get(command.service_id)
        if service is None:
            raise NotFoundError("Service not found")

        start_at = command.start_at
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
            start_at=start_at,
            end_at=end_at,
            created_at=now,
            updated_at=now,
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
