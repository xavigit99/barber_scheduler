from datetime import timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.handlers.availability.availability_service import (
    get_available_slots_payload,
)
from backend.application.queries.get_available_dates_query import GetAvailableDatesQuery


class GetAvailableDatesHandler(RequestHandler[GetAvailableDatesQuery, dict]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetAvailableDatesQuery) -> dict:
        dates: list = []
        current_date = query.start_date

        while current_date <= query.end_date:
            payload = get_available_slots_payload(
                self.db,
                barber_id=query.barber_id,
                service_id=query.service_id,
                target_date=current_date,
                timezone=query.timezone,
            )
            if payload["slots"]:
                dates.append(current_date)
            current_date += timedelta(days=1)

        return {
            "barber_id": query.barber_id,
            "service_id": query.service_id,
            "start_date": query.start_date,
            "end_date": query.end_date,
            "timezone": query.timezone,
            "dates": dates,
        }
