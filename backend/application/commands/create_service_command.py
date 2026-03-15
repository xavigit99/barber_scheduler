from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateServiceCommand(Request):
    name: str
    duration_minutes: int
    price: float
    tenant_id: int
