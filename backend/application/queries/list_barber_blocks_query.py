from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListBarberBlocksQuery(Request):
    barber_id: int
