from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_barber_availabilities_query import (
    ListBarberAvailabilitiesQuery,
)
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.exceptions import NotFoundError
from repositories.base_repository import BaseRepository


class ListBarberAvailabilitiesHandler(RequestHandler[ListBarberAvailabilitiesQuery, list]):

    def __init__(self, db: Session):
        self.db = db
        self.barber_repository = BaseRepository(Barber, db)

    async def handle(self, query: ListBarberAvailabilitiesQuery) -> list:
        if self.barber_repository.get(query.barber_id) is None:
            raise NotFoundError("Barber not found")

        return (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == query.barber_id,
                BarberAvailability.deleted.is_(False),
            )
            .order_by(BarberAvailability.weekday, BarberAvailability.start_time)
            .all()
        )
