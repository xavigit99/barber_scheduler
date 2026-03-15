from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteBarbershopCommand(Request):
    barbershop_id: int
