from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_services_query import ListServicesQuery
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class ListServicesHandler(RequestHandler[ListServicesQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListServicesQuery) -> list:
        repository = BaseRepository(Service, self.db, tenant_id=query.tenant_id)
        return repository.list()
