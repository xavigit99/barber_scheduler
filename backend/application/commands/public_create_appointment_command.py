from dataclasses import dataclass
from datetime import datetime

from diator.requests import Request


@dataclass(frozen=True)
class PublicCreateAppointmentCommand(Request):
    barber_id: int
    service_id: int
    start_at: datetime
    tenant_id: int
    client_name: str
    client_email: str
    client_phone: str
