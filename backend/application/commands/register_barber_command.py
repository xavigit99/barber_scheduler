from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class RegisterBarberCommand(Request):
    username: str
    email: str
    password: str
    nome: str
    telefone: str | None
    tenant_id: int
