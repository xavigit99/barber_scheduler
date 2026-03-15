from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteBarberBlockCommand(Request):
    barber_id: int
    block_id: int
