from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpdateProductCommand(Request):
    product_id: int
    nome: str | None = None
    descricao: str | None = None
    stock_atual: int | None = None
    stock_minimo: int | None = None
    preco_unitario: float | None = None
    tenant_id: int | None = None
