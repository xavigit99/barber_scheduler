from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_barber_block_command import DeleteBarberBlockCommand
from backend.core.barber import Barber
from backend.core.barber_block import BarberBlock
from repositories.base_repository import BaseRepository


class DeleteBarberBlockHandler(RequestHandler[DeleteBarberBlockCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteBarberBlockCommand) -> bool:
        if BaseRepository(Barber, self.db, tenant_id=command.tenant_id).get(command.barber_id) is None:
            return False

        block = (
            self.db.query(BarberBlock)
            .filter(
                BarberBlock.barber_id == command.barber_id,
                BarberBlock.deleted.is_(False),
                BarberBlock.id == command.block_id,
            )
            .first()
        )
        if block is None:
            return False

        block.deleted = True
        block.deleted_at = datetime.now(UTC)
        self.db.commit()
        return True
