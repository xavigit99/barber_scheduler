import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AppointmentNotification:
    client_name: str
    client_email: str
    barber_name: str
    service_name: str
    start_at: datetime
    appointment_id: int


class NotificationService(ABC):
    @abstractmethod
    def send_confirmation(self, notif: AppointmentNotification) -> None: ...

    @abstractmethod
    def send_cancellation(self, notif: AppointmentNotification) -> None: ...

    @abstractmethod
    def send_reschedule(self, notif: AppointmentNotification) -> None: ...


class LogNotificationService(NotificationService):
    """Log-based implementation — replace with real email/SMS in production."""

    def send_confirmation(self, notif: AppointmentNotification) -> None:
        logger.info(
            "Appointment confirmation",
            extra={
                "event": "appointment.confirmed",
                "appointment_id": notif.appointment_id,
                "client_email": notif.client_email,
                "client_name": notif.client_name,
                "barber": notif.barber_name,
                "service": notif.service_name,
                "start_at": notif.start_at.isoformat(),
            },
        )

    def send_cancellation(self, notif: AppointmentNotification) -> None:
        logger.info(
            "Appointment cancellation",
            extra={
                "event": "appointment.cancelled",
                "appointment_id": notif.appointment_id,
                "client_email": notif.client_email,
                "start_at": notif.start_at.isoformat(),
            },
        )

    def send_reschedule(self, notif: AppointmentNotification) -> None:
        logger.info(
            "Appointment rescheduled",
            extra={
                "event": "appointment.rescheduled",
                "appointment_id": notif.appointment_id,
                "client_email": notif.client_email,
                "new_start_at": notif.start_at.isoformat(),
            },
        )


# Singleton — swap for a real implementation via env/DI
_notification_service: NotificationService = LogNotificationService()


def get_notification_service() -> NotificationService:
    return _notification_service


def set_notification_service(service: NotificationService) -> None:
    global _notification_service
    _notification_service = service
