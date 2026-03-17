from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListBarberFeedbackQuery(Request):
    barber_id: int
    tenant_id: int | None = None
