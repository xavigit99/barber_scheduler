from sqlalchemy.orm import Session

from backend.application.queries.list_barbershops_query import ListBarbershopsQuery
from backend.core.barbershop import Barbershop
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class ListBarbershopsHandler(RequestHandler[ListBarbershopsQuery, list]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Barbershop, db)

    async def handle(self, query: ListBarbershopsQuery) -> list:
        return self.repository.list()
