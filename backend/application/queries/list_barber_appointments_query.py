from dataclasses import dataclass
from datetime import date
from typing import Optional

from diator.requests import Request


@dataclass(frozen=True)
class ListBarberAppointmentsQuery(Request):
    barber_id: int
    target_date: Optional[date] = None
    tenant_id: Optional[int] = None
