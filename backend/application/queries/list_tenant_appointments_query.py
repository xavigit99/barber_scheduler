from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class ListTenantAppointmentsQuery(Request):
    tenant_id: int
    barber_id: int | None = None
    target_date: date | None = None
