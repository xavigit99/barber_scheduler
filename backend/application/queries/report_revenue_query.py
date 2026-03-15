from dataclasses import dataclass
from datetime import date

from diator.requests import Request


@dataclass(frozen=True)
class ReportRevenueQuery(Request):
    start_date: date
    end_date: date
    tenant_id: int
