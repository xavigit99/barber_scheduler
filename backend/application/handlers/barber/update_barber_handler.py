from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.update_barber_command import UpdateBarberCommand
from backend.core.barber import Barber
from repositories.base_repository import BaseRepository


class UpdateBarberHandler(RequestHandler[UpdateBarberCommand, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: UpdateBarberCommand):
        update_data = {}

        if command.name is not None:
            update_data["nome"] = command.name
        if command.email is not None:
            update_data["email"] = command.email
        if command.phone is not None:
            update_data["telefone"] = command.phone
        if command.tenant_id is not None:
            update_data["tenant_id"] = command.tenant_id

        repository = BaseRepository(Barber, self.db, tenant_id=command.tenant_id)
        return repository.update(command.barber_id, update_data)
