from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_barber_availability_command import (
    CreateBarberAvailabilityCommand,
)
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.exceptions import NotFoundError
from backend.core.scheduling import (
    ensure_no_availability_overlap,
    validate_time_range,
    validate_weekday,
)
from repositories.base_repository import BaseRepository


class CreateBarberAvailabilityHandler(RequestHandler[CreateBarberAvailabilityCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateBarberAvailabilityCommand):
        if BaseRepository(Barber, self.db, tenant_id=command.tenant_id).get(command.barber_id) is None:
            raise NotFoundError("Barber not found")

        validate_weekday(command.weekday)
        validate_time_range(command.start_time, command.end_time)

        existing_availabilities = (
            self.db.query(BarberAvailability)
            .filter(
                BarberAvailability.barber_id == command.barber_id,
                BarberAvailability.deleted.is_(False),
                BarberAvailability.weekday == command.weekday,
            )
            .all()
        )
        ensure_no_availability_overlap(
            existing_availabilities,
            weekday=command.weekday,
            start_time=command.start_time,
            end_time=command.end_time,
        )

        return BaseRepository(BarberAvailability, self.db).create(
            {
                "barber_id": command.barber_id,
                "weekday": command.weekday,
                "start_time": command.start_time,
                "end_time": command.end_time,
            }
        )
