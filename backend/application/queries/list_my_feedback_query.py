from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListMyFeedbackQuery(Request):
    user_id: int
    tenant_id: int | None = None
