from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpdateBarberCommand(Request):
    barber_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    tenant_id: int | None = None
