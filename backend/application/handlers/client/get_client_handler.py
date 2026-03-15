from sqlalchemy.orm import Session

from backend.application.queries.get_client_query import GetClientQuery
from backend.core.client import Client
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class GetClientHandler(RequestHandler[GetClientQuery, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetClientQuery):
        repository = BaseRepository(Client, self.db, tenant_id=query.tenant_id)
        return repository.get(query.client_id)
