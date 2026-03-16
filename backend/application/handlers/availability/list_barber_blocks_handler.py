from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_barber_blocks_query import ListBarberBlocksQuery
from backend.core.barber import Barber
from backend.core.barber_block import BarberBlock
from backend.core.exceptions import NotFoundError
from repositories.base_repository import BaseRepository


class ListBarberBlocksHandler(RequestHandler[ListBarberBlocksQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListBarberBlocksQuery) -> list:
        if BaseRepository(Barber, self.db, tenant_id=query.tenant_id).get(query.barber_id) is None:
            raise NotFoundError("Barber not found")

        return (
            self.db.query(BarberBlock)
            .filter(
                BarberBlock.barber_id == query.barber_id,
                BarberBlock.deleted.is_(False),
            )
            .order_by(BarberBlock.start_at)
            .all()
        )
