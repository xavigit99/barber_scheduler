from datetime import datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_recurring_appointment_command import (
    CreateRecurringAppointmentCommand,
)
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.client import Client
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.service import Service
from repositories.base_repository import BaseRepository

ALLOWED_RECURRENCES = {"weekly", "biweekly"}


class CreateRecurringAppointmentHandler(
    RequestHandler[CreateRecurringAppointmentCommand, dict],
):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateRecurringAppointmentCommand) -> dict:
        if command.recurrence not in ALLOWED_RECURRENCES:
            raise ValidationError(
                f"Invalid recurrence: {command.recurrence}. Must be weekly or biweekly."
            )
        if command.count < 1 or command.count > 12:
            raise ValidationError("Count must be between 1 and 12")

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

        weeks_delta = 1 if command.recurrence == "weekly" else 2
        duration = timedelta(minutes=service.duracao_minutos)

        created: list[Appointment] = []
        skipped_count = 0

        for i in range(command.count):
            slot_start = command.start_at + timedelta(weeks=weeks_delta * i)
            slot_end = slot_start + duration

            # Check for conflicts (same pattern as create_appointment_handler)
            overlapping = (
                self.db.query(Appointment)
                .filter(
                    Appointment.barber_id == command.barber_id,
                    Appointment.deleted.is_(False),
                    Appointment.start_at < slot_end,
                    Appointment.end_at > slot_start,
                )
                .first()
            )
            if overlapping:
                skipped_count += 1
                continue

            now = datetime.now()
            appointment = Appointment(
                barber_id=command.barber_id,
                client_id=command.client_id,
                service_id=command.service_id,
                tenant_id=tenant_id,
                start_at=slot_start,
                end_at=slot_end,
                created_at=now,
                updated_at=now,
            )
            created.append(appointment)

        if created:
            self.db.add_all(created)
            self.db.commit()
            for appt in created:
                self.db.refresh(appt)

            # Fire webhooks for each created appointment (best-effort)
            try:
                from backend.core.webhook_dispatcher import dispatch_webhook_event

                for appt in created:
                    dispatch_webhook_event(self.db, appt.tenant_id, "appointment.created", {
                        "event": "appointment.created", "appointment_id": appt.id,
                        "tenant_id": appt.tenant_id, "barber_id": appt.barber_id,
                        "client_id": appt.client_id, "service_id": appt.service_id,
                        "start_at": appt.start_at.isoformat(), "end_at": appt.end_at.isoformat(),
                    })
            except Exception:  # noqa: BLE001
                pass

            # Notify barber via WhatsApp for each created appointment (best-effort)
            try:
                from backend.core.whatsapp import build_whatsapp_service

                if barber.telefone:
                    whatsapp = build_whatsapp_service()
                    for appt in created:
                        whatsapp.notify_barber_new_appointment(
                            barber_phone=barber.telefone,
                            barber_name=barber.nome,
                            client_name=client.nome,
                            service_name=service.nome,
                            start_at=appt.start_at,
                            appointment_id=appt.id,
                        )
            except Exception:  # noqa: BLE001
                pass


        return {"created": created, "skipped_count": skipped_count}
