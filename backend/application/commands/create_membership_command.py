from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateMembershipCommand(Request):
    barber_id: int
    barbershop_id: int
    role: str
    tenant_id: int
