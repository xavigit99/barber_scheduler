from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_service_query import GetServiceQuery
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class GetServiceHandler(RequestHandler[GetServiceQuery, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetServiceQuery):
        repository = BaseRepository(Service, self.db, tenant_id=query.tenant_id)
        return repository.get(query.service_id)
