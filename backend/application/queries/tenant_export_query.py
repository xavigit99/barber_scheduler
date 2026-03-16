from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class TenantExportQuery(Request):
    tenant_id: int
