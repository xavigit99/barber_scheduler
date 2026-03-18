from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateServicePackCommand(Request):
    nome: str
    service_id: int
    n_sessoes: int
    preco: float
    tenant_id: int | None = None
