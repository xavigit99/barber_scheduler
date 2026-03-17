from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateFeedbackCommand(Request):
    appointment_id: int
    rating: int
    user_id: int
    tenant_id: int | None = None
    comentario: str | None = None
