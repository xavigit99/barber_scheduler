from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetBarberQuery(Request):
    barber_id: int
    tenant_id: int
