from sqlalchemy.orm import Session

from backend.application.queries.get_barber_query import GetBarberQuery
from backend.core.barber import Barber
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class GetBarberHandler(RequestHandler[GetBarberQuery, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetBarberQuery):
        repository = BaseRepository(Barber, self.db, tenant_id=query.tenant_id)
        return repository.get(query.barber_id)
