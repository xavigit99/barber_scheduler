from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class TenantStatsQuery(Request):
    tenant_id: int
