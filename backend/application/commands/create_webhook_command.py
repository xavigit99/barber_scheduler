from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateWebhookCommand(Request):
    tenant_id: int
    url: str
    secret: str
    events: list[str]
