from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListWebhooksQuery(Request):
    tenant_id: int
