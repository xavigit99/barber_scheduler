from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.purchase_client_pack_command import PurchaseClientPackCommand
from backend.core.client import Client
from backend.core.exceptions import NotFoundError
from backend.core.service_pack import ClientPack, ServicePack
from repositories.base_repository import BaseRepository


class PurchaseClientPackHandler(RequestHandler[PurchaseClientPackCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: PurchaseClientPackCommand):
        client_repo = BaseRepository(Client, self.db, command.tenant_id)
        if client_repo.get(command.client_id) is None:
            raise NotFoundError("Client not found")

        pack = (
            self.db.query(ServicePack)
            .filter(
                ServicePack.id == command.service_pack_id,
                ServicePack.deleted.is_(False),
            )
            .first()
        )
        if pack is None:
            raise NotFoundError("Service pack not found")

        client_pack = ClientPack(
            client_id=command.client_id,
            service_pack_id=command.service_pack_id,
            tenant_id=command.tenant_id,
            sessoes_restantes=pack.n_sessoes,
            comprado_em=datetime.now(),
            expira_em=command.expira_em,
        )
        self.db.add(client_pack)
        self.db.commit()
        self.db.refresh(client_pack)
        return client_pack
