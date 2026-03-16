from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_barbershop_command import DeleteBarbershopCommand
from backend.core.barbershop import Barbershop
from repositories.base_repository import BaseRepository


class DeleteBarbershopHandler(RequestHandler[DeleteBarbershopCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteBarbershopCommand) -> bool:
        return BaseRepository(Barbershop, self.db, tenant_id=command.tenant_id).delete(command.barbershop_id)
