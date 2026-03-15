from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteServiceCommand(Request):
    service_id: int
    tenant_id: int
