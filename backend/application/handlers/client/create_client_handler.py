from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_client_command import CreateClientCommand
from backend.core.client import Client
from repositories.base_repository import BaseRepository


class CreateClientHandler(RequestHandler[CreateClientCommand, dict]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Client, db)

    async def handle(self, command: CreateClientCommand):
        return self.repository.create(
            {
                "nome": command.name,
                "email": command.email,
                "telefone": command.phone,
                "tenant_id": command.tenant_id,
            }
        )
