from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class PurchaseClientPackCommand(Request):
    client_id: int
    service_pack_id: int
    tenant_id: int | None = None
    expira_em: date | None = None
