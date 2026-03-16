from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_barbershop_query import GetBarbershopQuery
from backend.core.barbershop import Barbershop
from repositories.base_repository import BaseRepository


class GetBarbershopHandler(RequestHandler[GetBarbershopQuery, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetBarbershopQuery):
        return BaseRepository(Barbershop, self.db, tenant_id=query.tenant_id).get(query.barbershop_id)
