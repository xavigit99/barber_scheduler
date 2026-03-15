from sqlalchemy.orm import Session

from backend.application.commands.create_barber_command import CreateBarberCommand
from backend.core.barber import Barber
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class CreateBarberHandler(RequestHandler[CreateBarberCommand, dict]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateBarberCommand):
        repository = BaseRepository(Barber, self.db, tenant_id=command.tenant_id)
        return repository.create(
            {
                "nome": command.name,
                "email": command.email,
                "telefone": command.phone,
                "tenant_id": command.tenant_id,
            }
        )
