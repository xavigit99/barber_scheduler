from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class ListClientAppointmentsQuery(Request):
    client_id: int
    target_date: date | None = None
