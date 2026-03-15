from sqlalchemy.orm import Session

from backend.application.commands.update_barbershop_command import UpdateBarbershopCommand
from backend.core.barbershop import Barbershop
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class UpdateBarbershopHandler(RequestHandler[UpdateBarbershopCommand, object | None]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Barbershop, db)

    async def handle(self, command: UpdateBarbershopCommand):
        update_data = {}

        if command.name is not None:
            update_data["nome"] = command.name

        return self.repository.update(command.barbershop_id, update_data)
