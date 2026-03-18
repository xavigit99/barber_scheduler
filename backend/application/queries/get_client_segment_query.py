from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetClientSegmentQuery(Request):
    tenant_id: int
    inactive_days: int | None = None
    min_spend: float | None = None
    service_id: int | None = None
    has_birthday_this_month: bool | None = None
