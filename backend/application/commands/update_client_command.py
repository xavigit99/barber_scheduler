from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpdateClientCommand(Request):
    client_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
