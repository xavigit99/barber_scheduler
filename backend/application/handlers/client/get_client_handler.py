from sqlalchemy.orm import Session

from backend.application.queries.get_client_query import GetClientQuery
from backend.core.client import Cliente
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class GetClientHandler(RequestHandler[GetClientQuery, object | None]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Cliente, db)

    async def handle(self, query: GetClientQuery):
        return self.repository.get(query.client_id)
