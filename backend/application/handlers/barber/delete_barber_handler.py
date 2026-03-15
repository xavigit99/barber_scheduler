from sqlalchemy.orm import Session

from backend.application.commands.delete_barber_command import DeleteBarberCommand
from backend.core.barber import Barber
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class DeleteBarberHandler(RequestHandler[DeleteBarberCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteBarberCommand) -> bool:
        repository = BaseRepository(Barber, self.db, tenant_id=command.tenant_id)
        return repository.delete(command.barber_id)
