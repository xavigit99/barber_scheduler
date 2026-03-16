from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteBarberAvailabilityCommand(Request):
    barber_id: int
    availability_id: int
    tenant_id: int | None = None
