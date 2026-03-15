from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListBarbersQuery(Request):
    tenant_id: int
