from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListBarbershopsQuery(Request):
    tenant_id: int | None = None
