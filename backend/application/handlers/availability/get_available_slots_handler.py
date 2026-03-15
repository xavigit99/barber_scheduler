from datetime import datetime, time, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_available_slots_query import GetAvailableSlotsQuery
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.barber_block import BarberBlock
from backend.core.exceptions import NotFoundError
from backend.core.scheduling import build_daily_slots
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class GetAvailableSlotsHandler(RequestHandler[GetAvailableSlotsQuery, dict]):

    def __init__(self, db: Session):
        self.db = db
        self.barber_repository = BaseRepository(Barber, db)
        self.service_repository = BaseRepository(Service, db)

    async def handle(self, query: GetAvailableSlotsQuery) -> dict:
        if self.barber_repository.get(query.barber_id) is None:
            raise NotFoundError("Barber not found")

        service = self.service_repository.get(query.service_id)
        if service is None:
            raise NotFoundError("Service not found")

        availability_windows = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == query.barber_id,
                BarberAvailability.deleted.is_(False),
                BarberAvailability.weekday == query.target_date.weekday(),
            )
            .order_by(BarberAvailability.start_time)
            .all()
        )

        day_start = datetime.combine(query.target_date, time.min)
        day_end = day_start + timedelta(days=1)
        blocks = (
            self.db.query(BarberBlock)
            .filter(
                BarberBlock.barber_id == query.barber_id,
                BarberBlock.deleted.is_(False),
                BarberBlock.start_at < day_end,
                BarberBlock.end_at > day_start,
            )
            .order_by(BarberBlock.start_at)
            .all()
        )

        return {
            "barber_id": query.barber_id,
            "service_id": query.service_id,
            "data": query.target_date,
            "timezone": query.timezone,
            "slots": build_daily_slots(
                target_date=query.target_date,
                timezone_name=query.timezone,
                availability_windows=availability_windows,
                blocks=blocks,
                service_duration_minutes=service.duracao_minutos,
            ),
        }
