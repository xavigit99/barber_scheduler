import secrets
from datetime import datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_group_appointment_command import (
    CreateGroupAppointmentCommand,
)
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.client import Client
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class CreateGroupAppointmentHandler(RequestHandler[CreateGroupAppointmentCommand, dict]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateGroupAppointmentCommand) -> dict:
        if not command.client_ids:
            raise ValidationError("At least one client_id is required")

        tenant_id = command.tenant_id
        barber_repo = BaseRepository(Barber, self.db, tenant_id)
        service_repo = BaseRepository(Service, self.db, tenant_id)

        barber = barber_repo.get(command.barber_id)
        if barber is None:
            raise NotFoundError("Barber not found")

        service = service_repo.get(command.service_id)
        if service is None:
            raise NotFoundError("Service not found")

        if len(command.client_ids) > service.max_capacity:
            raise ValidationError(
                f"Number of clients ({len(command.client_ids)}) exceeds service capacity ({service.max_capacity})"
            )

        start_at = command.start_at
        end_at = start_at + timedelta(minutes=service.duracao_minutos)

        # Count existing bookings for this slot (capacity check)
        current_bookings = (
            self.db.query(Appointment)
            .filter(
                Appointment.barber_id == command.barber_id,
                Appointment.deleted.is_(False),
                Appointment.start_at < end_at,
                Appointment.end_at > start_at,
            )
            .count()
        )
        if current_bookings + len(command.client_ids) > service.max_capacity:
            raise ConflictError(
                f"Not enough capacity: {service.max_capacity - current_bookings} spots remaining"
            )

        group_id = command.group_id or secrets.token_hex(8)
        now = datetime.now()
        created: list[Appointment] = []

        for client_id in command.client_ids:
            client_repo = BaseRepository(Client, self.db, tenant_id)
            client = client_repo.get(client_id)
            if client is None:
                raise NotFoundError(f"Client {client_id} not found")

            token = secrets.token_urlsafe(32)
            appointment = Appointment(
                barber_id=command.barber_id,
                client_id=client_id,
                service_id=command.service_id,
                tenant_id=tenant_id,
                start_at=start_at,
                end_at=end_at,
                created_at=now,
                updated_at=now,
                status="pending",
                confirmation_token=token,
                group_id=group_id,
            )
            created.append(appointment)

        self.db.add_all(created)
        self.db.commit()
        for appt in created:
            self.db.refresh(appt)

        # Notify barber (best-effort)
        try:
            from backend.core.whatsapp import build_whatsapp_service

            if barber.telefone:
                wa = build_whatsapp_service()
                for appt in created:
                    client = self.db.query(Client).filter(Client.id == appt.client_id).first()
                    if client:
                        wa.notify_barber_new_appointment(
                            barber_phone=barber.telefone,
                            barber_name=barber.nome,
                            client_name=client.nome,
                            service_name=service.nome,
                            start_at=appt.start_at,
                            appointment_id=appt.id,
                        )
        except Exception:  # noqa: BLE001
            pass

        return {"created": created, "group_id": group_id}
