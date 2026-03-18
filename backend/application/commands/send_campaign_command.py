from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class SendCampaignCommand(Request):
    campaign_id: int
    tenant_id: int | None = None
