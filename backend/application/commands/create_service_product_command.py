from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateServiceProductCommand(Request):
    service_id: int
    product_id: int
    quantidade: int
    tenant_id: int | None = None
