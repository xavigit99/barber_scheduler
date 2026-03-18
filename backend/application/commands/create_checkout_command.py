from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateCheckoutCommand(Request):
    appointment_id: int
    tenant_id: int | None = None
