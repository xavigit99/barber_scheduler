from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class SaftExportQuery(Request):
    tenant_id: int
    year: int
