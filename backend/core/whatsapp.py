import logging
import os
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppService(ABC):

    @abstractmethod
    def notify_barber_new_appointment(
        self,
        barber_phone: str,
        barber_name: str,
        client_name: str,
        service_name: str,
        start_at: datetime,
        appointment_id: int,
    ) -> None: ...

    @abstractmethod
    def notify_barber_cancellation(
        self,
        barber_phone: str,
        barber_name: str,
        client_name: str,
        service_name: str,
        start_at: datetime,
        appointment_id: int,
    ) -> None: ...

    @abstractmethod
    def notify_barber_reschedule(
        self,
        barber_phone: str,
        barber_name: str,
        client_name: str,
        service_name: str,
        new_start_at: datetime,
        appointment_id: int,
    ) -> None: ...


class LogWhatsAppService(WhatsAppService):

    def notify_barber_new_appointment(self, barber_phone, barber_name, client_name, service_name, start_at, appointment_id):
        logger.info(
            "[WhatsApp] Novo agendamento → %s (%s): %s - %s às %s (id=%s)",
            barber_name, barber_phone, client_name, service_name, start_at, appointment_id,
        )

    def notify_barber_cancellation(self, barber_phone, barber_name, client_name, service_name, start_at, appointment_id):
        logger.info(
            "[WhatsApp] Cancelamento → %s (%s): %s - %s às %s (id=%s)",
            barber_name, barber_phone, client_name, service_name, start_at, appointment_id,
        )

    def notify_barber_reschedule(self, barber_phone, barber_name, client_name, service_name, new_start_at, appointment_id):
        logger.info(
            "[WhatsApp] Reagendamento → %s (%s): %s - %s nova hora: %s (id=%s)",
            barber_name, barber_phone, client_name, service_name, new_start_at, appointment_id,
        )


class CallMeBotWhatsAppService(WhatsAppService):
    """Free WhatsApp notifications via CallMeBot.

    Each barber must activate CallMeBot once:
    1. Add +34 644 59 96 19 to contacts
    2. Send "I allow callmebot to send me messages"
    3. Receive their personal apikey
    """

    _BASE_URL = "https://api.callmebot.com/whatsapp.php"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def _send(self, phone: str, text: str) -> None:
        phone = phone.lstrip("+")
        params = urllib.parse.urlencode({"phone": phone, "text": text, "apikey": self._api_key})
        url = f"{self._BASE_URL}?{params}"
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
            resp.read()

    def notify_barber_new_appointment(self, barber_phone, barber_name, client_name, service_name, start_at, appointment_id):
        self._send(
            barber_phone,
            f"Olá {barber_name}, novo agendamento: {client_name} - {service_name} às {start_at.strftime('%d/%m/%Y %H:%M')}.",
        )

    def notify_barber_cancellation(self, barber_phone, barber_name, client_name, service_name, start_at, appointment_id):
        self._send(
            barber_phone,
            f"Agendamento cancelado: {client_name} - {service_name} às {start_at.strftime('%d/%m/%Y %H:%M')}.",
        )

    def notify_barber_reschedule(self, barber_phone, barber_name, client_name, service_name, new_start_at, appointment_id):
        self._send(
            barber_phone,
            f"Agendamento reagendado: {client_name} - {service_name} nova hora: {new_start_at.strftime('%d/%m/%Y %H:%M')}.",
        )


def build_whatsapp_service() -> WhatsAppService:
    api_key = os.getenv("CALLMEBOT_API_KEY")
    if api_key:
        return CallMeBotWhatsAppService(api_key)
    return LogWhatsAppService()
