from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListServicesQuery(Request):
    tenant_id: int
