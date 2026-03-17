from datetime import UTC, datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.public_create_appointment_command import (
    PublicCreateAppointmentCommand,
)
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.barber_block import BarberBlock
from backend.core.client import Client
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.notifications import AppointmentNotification, get_notification_service
from backend.core.scheduling import build_daily_slots
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class PublicCreateAppointmentHandler(RequestHandler[PublicCreateAppointmentCommand, dict]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: PublicCreateAppointmentCommand) -> dict:
        repo_barber = BaseRepository(Barber, self.db, command.tenant_id)
        repo_service = BaseRepository(Service, self.db, command.tenant_id)
        repo_client = BaseRepository(Client, self.db, command.tenant_id)
        repo_appt = BaseRepository(Appointment, self.db, command.tenant_id)

        barber = repo_barber.get(command.barber_id)
        if not barber:
            raise NotFoundError(f"Barber {command.barber_id} not found")

        service = repo_service.get(command.service_id)
        if not service:
            raise NotFoundError(f"Service {command.service_id} not found")

        # Find or create client by email within tenant
        existing = (
            self.db.query(Client)
            .filter(
                Client.email == command.client_email,
                Client.tenant_id == command.tenant_id,
                Client.deleted.is_(False),
            )
            .first()
        )
        if existing:
            client = existing
        else:
            client = repo_client.create({
                "nome": command.client_name,
                "email": command.client_email,
                "telefone": command.client_phone,
                "tenant_id": command.tenant_id,
            })

        # Validate slot availability
        target_date = command.start_at.date()
        avail_windows = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == command.barber_id,
                BarberAvailability.deleted.is_(False),
            )
            .all()
        )
        blocks = (
            self.db.query(BarberBlock)
            .filter(
                BarberBlock.barber_id == command.barber_id,
                BarberBlock.deleted.is_(False),
            )
            .all()
        )
        slots = build_daily_slots(
            availability_windows=avail_windows,
            blocks=blocks,
            service_duration_minutes=service.duracao_minutos,
            target_date=target_date,
            timezone_name="Europe/Lisbon",
        )
        slot_starts = [s["inicio"] for s in slots]
        start_aware = command.start_at
        if start_aware.tzinfo is None:
            start_aware = start_aware.replace(tzinfo=UTC)
        if not any(abs((s - start_aware).total_seconds()) < 60 for s in slot_starts):
            raise ValidationError("Requested slot is not available")

        end_at = command.start_at + timedelta(minutes=service.duracao_minutos)

        # Check conflicts
        conflicts = (
            self.db.query(Appointment)
            .filter(
                Appointment.barber_id == command.barber_id,
                Appointment.deleted.is_(False),
                Appointment.start_at < end_at,
                Appointment.end_at > command.start_at,
            )
            .all()
        )
        if conflicts:
            raise ConflictError("Time slot already booked")

        now = datetime.now(UTC)
        appt = repo_appt.create({
            "barber_id": command.barber_id,
            "client_id": client.id,
            "service_id": command.service_id,
            "start_at": command.start_at,
            "end_at": end_at,
            "tenant_id": command.tenant_id,
            "created_at": now,
            "updated_at": now,
        })

        # Notify client
        get_notification_service().send_confirmation(
            AppointmentNotification(
                client_name=client.nome,
                client_email=client.email,
                barber_name=barber.nome,
                service_name=service.nome,
                start_at=command.start_at,
                appointment_id=appt.id,
            )
        )

        return {
            "id": appt.id,
            "barber_id": appt.barber_id,
            "client_id": appt.client_id,
            "service_id": appt.service_id,
            "start_at": appt.start_at,
            "end_at": appt.end_at,
            "client_name": client.nome,
            "client_email": client.email,
        }
