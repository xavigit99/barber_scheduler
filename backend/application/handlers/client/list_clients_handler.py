from sqlalchemy.orm import Session

from backend.application.queries.list_clients_query import ListClientsQuery
from backend.core.client import Cliente
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class ListClientsHandler(RequestHandler[ListClientsQuery, list]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Cliente, db)

    async def handle(self, query: ListClientsQuery) -> list:
        return self.repository.list()
