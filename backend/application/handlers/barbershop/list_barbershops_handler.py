from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_barbershops_query import ListBarbershopsQuery
from backend.core.barbershop import Barbershop
from repositories.base_repository import BaseRepository


class ListBarbershopsHandler(RequestHandler[ListBarbershopsQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListBarbershopsQuery) -> list:
        return BaseRepository(Barbershop, self.db, tenant_id=query.tenant_id).list()
