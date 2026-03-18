from dataclasses import dataclass
from datetime import datetime

from diator.requests import Request


@dataclass(frozen=True)
class CreateGroupAppointmentCommand(Request):
    barber_id: int
    service_id: int
    start_at: datetime
    client_ids: list[int]
    tenant_id: int | None = None
    group_id: str | None = None
