from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpdateServiceCommand(Request):
    service_id: int
    name: str | None = None
    duration_minutes: int | None = None
    price: float | None = None
    tenant_id: int | None = None
