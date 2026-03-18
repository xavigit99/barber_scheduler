from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_campaigns_query import ListCampaignsQuery
from backend.core.campaign import Campaign
from repositories.base_repository import BaseRepository


class ListCampaignsHandler(RequestHandler[ListCampaignsQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListCampaignsQuery) -> list:
        repository = BaseRepository(Campaign, self.db, tenant_id=query.tenant_id)
        return repository.list()
