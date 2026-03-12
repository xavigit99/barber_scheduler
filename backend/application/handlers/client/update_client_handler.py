from sqlalchemy.orm import Session

from backend.application.commands.update_client_command import UpdateClientCommand
from backend.core.client import Cliente
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class UpdateClientHandler(RequestHandler[UpdateClientCommand, object | None]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Cliente, db)

    async def handle(self, command: UpdateClientCommand):
        update_data = {}

        if command.name is not None:
            update_data["nome"] = command.name
        if command.email is not None:
            update_data["email"] = command.email
        if command.phone is not None:
            update_data["telefone"] = command.phone

        return self.repository.update(command.client_id, update_data)
