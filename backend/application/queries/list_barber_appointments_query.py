from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class ListBarberAppointmentsQuery(Request):
    barber_id: int
    target_date: date | None = None
    tenant_id: int | None = None
