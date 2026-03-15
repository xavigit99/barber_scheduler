from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetBarbershopQuery(Request):
    barbershop_id: int
