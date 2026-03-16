from dataclasses import dataclass
from datetime import datetime

from diator.requests import Request


@dataclass(frozen=True)
class CreateBarberBlockCommand(Request):
    barber_id: int
    kind: str
    start_at: datetime
    end_at: datetime
    reason: str | None = None
    tenant_id: int | None = None
