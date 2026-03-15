from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateBarbershopCommand(Request):
    name: str
    owner_user_id: int
