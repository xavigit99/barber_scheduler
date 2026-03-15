from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetServiceQuery(Request):
    service_id: int
    tenant_id: int
