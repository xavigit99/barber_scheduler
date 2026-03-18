from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListCampaignsQuery(Request):
    tenant_id: int
