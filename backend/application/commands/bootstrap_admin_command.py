from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class BootstrapAdminCommand(Request):
    username: str
    email: str
    password: str
