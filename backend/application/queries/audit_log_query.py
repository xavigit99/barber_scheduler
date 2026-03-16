from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class AuditLogQuery(Request):
    entity: str
    tenant_id: int
    from_date: date | None = None
    to_date: date | None = None
