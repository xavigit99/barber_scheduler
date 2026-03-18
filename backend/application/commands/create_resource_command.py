from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateResourceCommand(Request):
    nome: str
    tipo: str
    tenant_id: int | None = None
