from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListBarberAvailabilitiesQuery(Request):
    barber_id: int
