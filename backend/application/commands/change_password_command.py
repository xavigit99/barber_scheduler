from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ChangePasswordCommand(Request):
    user_id: int
    current_password: str
    new_password: str
