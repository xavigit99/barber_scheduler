from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListClientsQuery(Request):
    pass
