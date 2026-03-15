from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateBarberCommand(Request):
    name: str
    email: str
    tenant_id: int
    phone: str | None = None
