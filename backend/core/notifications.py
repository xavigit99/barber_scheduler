import logging
import os
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


@dataclass
class AppointmentNotification:
    client_name: str
    client_email: str
    barber_name: str
    service_name: str
    start_at: datetime
    appointment_id: int
    confirmation_token: str | None = None
    app_base_url: str | None = None


class NotificationService(ABC):
    @abstractmethod
    def send_confirmation(self, notif: AppointmentNotification) -> None: ...

    @abstractmethod
    def send_cancellation(self, notif: AppointmentNotification) -> None: ...

    @abstractmethod
    def send_reschedule(self, notif: AppointmentNotification) -> None: ...

    @abstractmethod
    def send_reminder(self, notif: AppointmentNotification) -> None: ...

    @abstractmethod
    def send_birthday(self, client_name: str, client_email: str) -> None: ...

    @abstractmethod
    def send_campaign(
        self,
        client_name: str,
        client_email: str,
        subject: str,
        body: str,
    ) -> None: ...


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

    def send_reminder(self, notif: AppointmentNotification) -> None:
        logger.info(
            "Appointment reminder",
            extra={
                "event": "appointment.reminder",
                "appointment_id": notif.appointment_id,
                "client_email": notif.client_email,
                "start_at": notif.start_at.isoformat(),
            },
        )

    def send_birthday(self, client_name: str, client_email: str) -> None:
        logger.info(
            "Birthday message",
            extra={"event": "client.birthday", "client_email": client_email},
        )

    def send_campaign(
        self,
        client_name: str,
        client_email: str,
        subject: str,
        body: str,
    ) -> None:
        logger.info(
            "Campaign email",
            extra={
                "event": "campaign.sent",
                "client_email": client_email,
                "subject": subject,
            },
        )


class SmtpNotificationService(NotificationService):
    """Sends emails via SMTP. Configured through environment variables."""

    def __init__(self, host: str, port: int, username: str, password: str, sender: str, use_tls: bool = True) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender
        self.use_tls = use_tls

    def _send(self, to: str, subject: str, body: str) -> None:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = to
        with smtplib.SMTP(self.host, self.port) as smtp:
            if self.use_tls:
                smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, [to], msg.as_string())

    def send_confirmation(self, notif: AppointmentNotification) -> None:
        confirm_section = ""
        if notif.confirmation_token and notif.app_base_url:
            confirm_url = f"{notif.app_base_url}/appointments/confirm/{notif.confirmation_token}"
            confirm_section = (
                f"\nConfirme a sua presença clicando no link abaixo:\n"
                f"  {confirm_url}\n"
            )
        self._send(
            to=notif.client_email,
            subject=f"Agendamento confirmado — {notif.service_name} com {notif.barber_name}",
            body=(
                f"Olá {notif.client_name},\n\n"
                f"O seu agendamento foi confirmado.\n\n"
                f"  Serviço:  {notif.service_name}\n"
                f"  Barbeiro: {notif.barber_name}\n"
                f"  Data:     {notif.start_at:%d/%m/%Y às %H:%M}\n"
                f"{confirm_section}\n"
                f"ID do agendamento: #{notif.appointment_id}\n"
            ),
        )

    def send_cancellation(self, notif: AppointmentNotification) -> None:
        self._send(
            to=notif.client_email,
            subject=f"Agendamento cancelado — {notif.service_name}",
            body=(
                f"Olá {notif.client_name},\n\n"
                f"O seu agendamento foi cancelado.\n\n"
                f"  Serviço:  {notif.service_name}\n"
                f"  Barbeiro: {notif.barber_name}\n"
                f"  Data:     {notif.start_at:%d/%m/%Y às %H:%M}\n\n"
                f"Se não foi você a cancelar, contacte-nos.\n"
            ),
        )

    def send_reschedule(self, notif: AppointmentNotification) -> None:
        self._send(
            to=notif.client_email,
            subject=f"Agendamento remarcado — {notif.service_name} com {notif.barber_name}",
            body=(
                f"Olá {notif.client_name},\n\n"
                f"O seu agendamento foi remarcado.\n\n"
                f"  Serviço:  {notif.service_name}\n"
                f"  Barbeiro: {notif.barber_name}\n"
                f"  Nova data: {notif.start_at:%d/%m/%Y às %H:%M}\n\n"
                f"ID do agendamento: #{notif.appointment_id}\n"
            ),
        )

    def send_reminder(self, notif: AppointmentNotification) -> None:
        self._send(
            to=notif.client_email,
            subject=f"Lembrete: {notif.service_name} amanhã com {notif.barber_name}",
            body=(
                f"Olá {notif.client_name},\n\n"
                f"Este é um lembrete do seu agendamento de amanhã.\n\n"
                f"  Serviço:  {notif.service_name}\n"
                f"  Barbeiro: {notif.barber_name}\n"
                f"  Data:     {notif.start_at:%d/%m/%Y às %H:%M}\n\n"
                f"ID do agendamento: #{notif.appointment_id}\n"
            ),
        )

    def send_birthday(self, client_name: str, client_email: str) -> None:
        self._send(
            to=client_email,
            subject=f"Feliz Aniversário, {client_name}!",
            body=(
                f"Olá {client_name},\n\n"
                f"A toda a equipa deseja-lhe um feliz aniversário! 🎉\n\n"
                f"Como presente, tem 10% de desconto no próximo agendamento.\n"
                f"Basta mencionar este email ao marcar.\n\n"
                f"Com os melhores cumprimentos,\n"
                f"A equipa\n"
            ),
        )

    def send_campaign(
        self,
        client_name: str,
        client_email: str,
        subject: str,
        body: str,
    ) -> None:
        self._send(to=client_email, subject=subject, body=body)


def build_notification_service() -> NotificationService:
    """Factory — returns SmtpNotificationService if SMTP_HOST is set, else LogNotificationService."""
    host = os.getenv("SMTP_HOST", "")
    if not host:
        logger.warning("SMTP_HOST not configured — using log-only notifications")
        return LogNotificationService()
    return SmtpNotificationService(
        host=host,
        port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("SMTP_USERNAME", ""),
        password=os.getenv("SMTP_PASSWORD", ""),
        sender=os.getenv("SMTP_SENDER", "noreply@barberpro.app"),
        use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    )


# Singleton — swap for a real implementation via env/DI
_notification_service: NotificationService = LogNotificationService()


def get_notification_service() -> NotificationService:
    return _notification_service


def set_notification_service(service: NotificationService) -> None:
    global _notification_service
    _notification_service = service
