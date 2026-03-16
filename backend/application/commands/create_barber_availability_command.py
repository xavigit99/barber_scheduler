from dataclasses import dataclass
from datetime import time

from diator.requests import Request


@dataclass(frozen=True)
class CreateBarberAvailabilityCommand(Request):
    barber_id: int
    weekday: int
    start_time: time
    end_time: time
    tenant_id: int | None = None
