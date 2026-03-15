from sqlalchemy.orm import Session

from backend.application.commands.delete_barbershop_command import DeleteBarbershopCommand
from backend.core.barbershop import Barbershop
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class DeleteBarbershopHandler(RequestHandler[DeleteBarbershopCommand, bool]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Barbershop, db)

    async def handle(self, command: DeleteBarbershopCommand) -> bool:
        return self.repository.delete(command.barbershop_id)
