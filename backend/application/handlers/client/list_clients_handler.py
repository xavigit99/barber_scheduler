from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_clients_query import ListClientsQuery
from backend.core.client import Client
from repositories.base_repository import BaseRepository


class ListClientsHandler(RequestHandler[ListClientsQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListClientsQuery) -> list:
        repository = BaseRepository(Client, self.db, tenant_id=query.tenant_id)
        return repository.list()
