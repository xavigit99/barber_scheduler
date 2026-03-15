from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_barbers_query import ListBarbersQuery
from backend.core.barber import Barber
from repositories.base_repository import BaseRepository


class ListBarbersHandler(RequestHandler[ListBarbersQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListBarbersQuery) -> list:
        repository = BaseRepository(Barber, self.db, tenant_id=query.tenant_id)
        return repository.list()
