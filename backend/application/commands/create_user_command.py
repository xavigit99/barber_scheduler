from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateUserCommand(Request):
    username: str
    email: str
    password: str
    role: str
