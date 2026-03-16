from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class RegisterClientCommand(Request):
    username: str
    email: str
    password: str
    nome: str
    tenant_id: int
