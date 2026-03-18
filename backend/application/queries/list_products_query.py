from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListProductsQuery(Request):
    tenant_id: int | None = None
    low_stock: bool = False
