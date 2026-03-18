from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListInvoicesQuery(Request):
    tenant_id: int
