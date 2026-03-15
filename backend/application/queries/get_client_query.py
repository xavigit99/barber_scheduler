from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetClientQuery(Request):
    client_id: int
    tenant_id: int
