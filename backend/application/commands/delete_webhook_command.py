from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteWebhookCommand(Request):
    webhook_id: int
    tenant_id: int
