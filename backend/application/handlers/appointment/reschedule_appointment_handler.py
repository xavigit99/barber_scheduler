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

        # Fire webhook (best-effort)
        try:
            from backend.core.webhook_dispatcher import dispatch_webhook_event

            dispatch_webhook_event(self.db, appointment.tenant_id, "appointment.rescheduled", {
                "event": "appointment.rescheduled", "appointment_id": appointment.id,
                "tenant_id": appointment.tenant_id, "barber_id": appointment.barber_id,
                "client_id": appointment.client_id, "service_id": appointment.service_id,
                "start_at": appointment.start_at.isoformat(), "end_at": appointment.end_at.isoformat(),
            })
        except Exception:  # noqa: BLE001
            pass

        # Best-effort reschedule notification
        from backend.core.notifications import AppointmentNotification, get_notification_service

        client = None
        barber = None
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

        # Notify barber via WhatsApp (best-effort)
        try:
            from backend.core.whatsapp import build_whatsapp_service

            if barber and barber.telefone:
                build_whatsapp_service().notify_barber_reschedule(
                    barber_phone=barber.telefone,
                    barber_name=barber.nome,
                    client_name=client.nome if client else "",
                    service_name=service.nome,
                    new_start_at=start_at,
                    appointment_id=appointment.id,
                )
        except Exception:  # noqa: BLE001
            pass

        return appointment
