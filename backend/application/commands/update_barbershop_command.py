from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpdateBarbershopCommand(Request):
    barbershop_id: int
    name: str | None = None
    tenant_id: int | None = None
