from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CreateCampaignCommand(Request):
    nome: str
    subject: str
    body_template: str
    segment_filters: str  # JSON string
    tenant_id: int | None = None
