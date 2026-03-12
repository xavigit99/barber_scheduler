from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateClientCommand(Request):
    name: str
    email: str
    phone: str | None = None
