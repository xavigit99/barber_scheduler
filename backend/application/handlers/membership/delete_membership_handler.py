from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_membership_command import DeleteMembershipCommand
from backend.core.barbershop import Barbershop
from backend.core.barbershop_membership import BarbershopMembership
from repositories.base_repository import BaseRepository


class DeleteMembershipHandler(RequestHandler[DeleteMembershipCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteMembershipCommand) -> bool:
        membership = (
            self.db.query(BarbershopMembership)
            .filter(
                BarbershopMembership.id == command.membership_id,
                BarbershopMembership.deleted.is_(False),
            )
            .first()
        )
        if membership is None:
            return False

        if membership.barbershop_id != command.barbershop_id:
            return False

        if BaseRepository(Barbershop, self.db, tenant_id=command.tenant_id).get(membership.barbershop_id) is None:
            return False

        membership.deleted = True
        membership.deleted_at = datetime.now(UTC)
        self.db.commit()
        return True
