from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_available_slots_query import GetAvailableSlotsQuery
from backend.application.handlers.availability.availability_service import (
    get_available_slots_payload,
)


class GetAvailableSlotsHandler(RequestHandler[GetAvailableSlotsQuery, dict]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetAvailableSlotsQuery) -> dict:
        return get_available_slots_payload(
            self.db,
            barber_id=query.barber_id,
            service_id=query.service_id,
            target_date=query.target_date,
            timezone=query.timezone,
        )
