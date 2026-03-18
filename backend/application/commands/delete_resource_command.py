from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteResourceCommand(Request):
    resource_id: int
    tenant_id: int | None = None
