from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteProductCommand(Request):
    product_id: int
    tenant_id: int | None = None
