from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateBillingPortalCommand(Request):
    barbershop_id: int
    owner_user_id: int
