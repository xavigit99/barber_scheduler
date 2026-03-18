from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateSubscriptionCheckoutCommand(Request):
    barbershop_id: int
    plan: str
    owner_user_id: int
