from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_service_command import CreateServiceCommand
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class CreateServiceHandler(RequestHandler[CreateServiceCommand, dict]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateServiceCommand):
        repository = BaseRepository(Service, self.db, tenant_id=command.tenant_id)
        return repository.create(
            {
                "nome": command.name,
                "duracao_minutos": command.duration_minutes,
                "preco": command.price,
                "tenant_id": command.tenant_id,
            }
        )
