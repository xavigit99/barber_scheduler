from sqlalchemy.orm import Session

from backend.application.commands.update_client_command import UpdateClientCommand
from backend.core.client import Client
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class UpdateClientHandler(RequestHandler[UpdateClientCommand, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: UpdateClientCommand):
        update_data = {}

        if command.name is not None:
            update_data["nome"] = command.name
        if command.email is not None:
            update_data["email"] = command.email
        if command.phone is not None:
            update_data["telefone"] = command.phone
        if command.tenant_id is not None:
            update_data["tenant_id"] = command.tenant_id

        repository = BaseRepository(Client, self.db, tenant_id=command.tenant_id)
        return repository.update(command.client_id, update_data)
