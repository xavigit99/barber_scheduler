from dataclasses import dataclass
from datetime import time

from diator.requests import Request


@dataclass(frozen=True)
class UpdateBarberAvailabilityCommand(Request):
    barber_id: int
    availability_id: int
    weekday: int | None = None
    start_time: time | None = None
    end_time: time | None = None
