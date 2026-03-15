from sqlalchemy.orm import Session

from backend.application.commands.update_service_command import UpdateServiceCommand
from backend.core.service import Service
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class UpdateServiceHandler(RequestHandler[UpdateServiceCommand, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: UpdateServiceCommand):
        update_data = {}

        if command.name is not None:
            update_data["nome"] = command.name
        if command.duration_minutes is not None:
            update_data["duracao_minutos"] = command.duration_minutes
        if command.price is not None:
            update_data["preco"] = command.price
        if command.tenant_id is not None:
            update_data["tenant_id"] = command.tenant_id

        repository = BaseRepository(Service, self.db, tenant_id=command.tenant_id)
        return repository.update(command.service_id, update_data)
