from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_barber_availability_command import (
    DeleteBarberAvailabilityCommand,
)
from backend.core.barber_availability import BarberAvailability


class DeleteBarberAvailabilityHandler(RequestHandler[DeleteBarberAvailabilityCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteBarberAvailabilityCommand) -> bool:
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
            return False

        availability.deleted = True
        self.db.commit()
        return True
