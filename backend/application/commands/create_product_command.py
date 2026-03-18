from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateProductCommand(Request):
    nome: str
    descricao: str | None
    stock_atual: int
    stock_minimo: int
    preco_unitario: float
    tenant_id: int | None = None
