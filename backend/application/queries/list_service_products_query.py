from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListServiceProductsQuery(Request):
    service_id: int
    tenant_id: int | None = None
