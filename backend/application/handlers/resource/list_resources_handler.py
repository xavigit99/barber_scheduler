from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_resources_query import ListResourcesQuery
from backend.core.resource import Resource
from repositories.base_repository import BaseRepository


class ListResourcesHandler(RequestHandler[ListResourcesQuery, list]):
    """Lists resources for a tenant (F38)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListResourcesQuery) -> list[Resource]:
        repo = BaseRepository(Resource, self.db, query.tenant_id)
        return repo.list()
