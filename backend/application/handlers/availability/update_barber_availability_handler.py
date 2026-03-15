from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.update_barber_availability_command import (
    UpdateBarberAvailabilityCommand,
)
from backend.core.barber_availability import BarberAvailability
from backend.core.exceptions import NotFoundError
from backend.core.scheduling import (
    ensure_no_availability_overlap,
    validate_time_range,
    validate_weekday,
)
from repositories.base_repository import BaseRepository


class UpdateBarberAvailabilityHandler(RequestHandler[UpdateBarberAvailabilityCommand, object]):

    def __init__(self, db: Session):
        self.db = db
        self.repository = BaseRepository(BarberAvailability, db)

    async def handle(self, command: UpdateBarberAvailabilityCommand):
        availability = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == command.barber_id,
                BarberAvailability.deleted.is_(False),
                BarberAvailability.id == command.availability_id,
            )
            .first()
        )
        if availability is None:
            raise NotFoundError("Availability window not found")

        weekday = command.weekday if command.weekday is not None else availability.weekday
        start_time = command.start_time if command.start_time is not None else availability.start_time
        end_time = command.end_time if command.end_time is not None else availability.end_time

        validate_weekday(weekday)
        validate_time_range(start_time, end_time)

        existing_availabilities = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == command.barber_id,
                BarberAvailability.deleted.is_(False),
                BarberAvailability.weekday == weekday,
            )
            .all()
        )
        ensure_no_availability_overlap(
            existing_availabilities,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            exclude_availability_id=availability.id,
        )

        update_data = {
            "weekday": weekday,
            "start_time": start_time,
            "end_time": end_time,
        }
        return self.repository.update(command.availability_id, update_data)
