from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class PurgeDeletedCommand(Request):
    entity: str
    older_than_days: int
    tenant_id: int
