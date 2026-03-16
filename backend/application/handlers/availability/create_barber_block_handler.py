from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_barber_block_command import CreateBarberBlockCommand
from backend.core.barber import Barber
from backend.core.barber_block import BarberBlock
from backend.core.exceptions import NotFoundError
from backend.core.scheduling import (
    validate_block_kind,
    validate_datetime_range,
)
from repositories.base_repository import BaseRepository


class CreateBarberBlockHandler(RequestHandler[CreateBarberBlockCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateBarberBlockCommand):
        if BaseRepository(Barber, self.db, tenant_id=command.tenant_id).get(command.barber_id) is None:
            raise NotFoundError("Barber not found")

        validate_block_kind(command.kind)
        validate_datetime_range(command.start_at, command.end_at)

        return BaseRepository(BarberBlock, self.db).create(
            {
                "barber_id": command.barber_id,
                "kind": command.kind,
                "start_at": command.start_at,
                "end_at": command.end_at,
                "reason": command.reason,
            }
        )
