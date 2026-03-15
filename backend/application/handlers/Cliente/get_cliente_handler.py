from sqlalchemy.orm import Session
from diator.requests import RequestHandler

from backend.application.queries.get_clientes_query import GetClientesQuery
from backend.core.client import Cliente

class GetClientesHandler(
    RequestHandler[GetClientesQuery, list]
):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetClientesQuery) -> list:
        return self.db.query(Cliente).all()