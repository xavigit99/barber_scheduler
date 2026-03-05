from dataclasses import dataclass
from diator.requests import Request


@dataclass(frozen=True)
class CreateClienteCommand(Request):
    nome: str
    email: str
    telefone: str | None = None