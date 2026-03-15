from dataclasses import dataclass
from datetime import datetime

from diator.requests import Request


@dataclass(frozen=True)
class RescheduleAppointmentCommand(Request):
    appointment_id: int
    start_at: datetime
