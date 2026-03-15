from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class ReportDailyQuery(Request):
    target_date: date
    tenant_id: int
