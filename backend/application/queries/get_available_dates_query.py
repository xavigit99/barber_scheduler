from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class GetAvailableDatesQuery(Request):
    barber_id: int
    service_id: int
    start_date: date
    end_date: date
    timezone: str
