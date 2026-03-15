from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteBarberCommand(Request):
    barber_id: int
    tenant_id: int
