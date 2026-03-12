from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteClientCommand(Request):
    client_id: int
