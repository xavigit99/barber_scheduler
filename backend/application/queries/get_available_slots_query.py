from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class GetAvailableSlotsQuery(Request):
    barber_id: int
    service_id: int
    target_date: date
    timezone: str
