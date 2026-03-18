from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_service_pack_command import CreateServicePackCommand
from backend.core.exceptions import NotFoundError
from backend.core.service import Service
from backend.core.service_pack import ServicePack
from repositories.base_repository import BaseRepository


class CreateServicePackHandler(RequestHandler[CreateServicePackCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateServicePackCommand):
        service_repo = BaseRepository(Service, self.db, command.tenant_id)
        if service_repo.get(command.service_id) is None:
            raise NotFoundError("Service not found")

        pack = ServicePack(
            nome=command.nome,
            service_id=command.service_id,
            tenant_id=command.tenant_id,
            n_sessoes=command.n_sessoes,
            preco=command.preco,
        )
        self.db.add(pack)
        self.db.commit()
        self.db.refresh(pack)
        return pack
