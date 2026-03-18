from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_campaign_query import GetCampaignQuery
from backend.core.campaign import Campaign
from repositories.base_repository import BaseRepository


class GetCampaignHandler(RequestHandler[GetCampaignQuery, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetCampaignQuery) -> Campaign | None:
        repository = BaseRepository(Campaign, self.db, tenant_id=query.tenant_id)
        return repository.get(query.campaign_id)
