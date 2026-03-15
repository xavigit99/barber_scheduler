from dataclasses import dataclass
from datetime import datetime

from diator.requests import Request


@dataclass(frozen=True)
class CreateAppointmentCommand(Request):
    barber_id: int
    client_id: int
    service_id: int
    start_at: datetime
