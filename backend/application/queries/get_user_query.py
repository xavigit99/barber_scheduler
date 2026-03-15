from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetUserQuery(Request):
    user_id: int
