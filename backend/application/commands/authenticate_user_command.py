from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class AuthenticateUserCommand(Request):
    username: str
    password: str
