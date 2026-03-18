from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateInvoiceCommand(Request):
    appointment_id: int
    tenant_id: int | None = None
