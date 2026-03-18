from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class AdjustStockCommand(Request):
    product_id: int
    delta: int
    reason: str
    tenant_id: int | None = None
