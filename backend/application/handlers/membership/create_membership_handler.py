from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_membership_command import CreateMembershipCommand
from backend.core.barber import Barber
from backend.core.barbershop import Barbershop
from backend.core.barbershop_membership import BarbershopMembership
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.membership_roles import ALLOWED_MEMBERSHIP_ROLES
from repositories.base_repository import BaseRepository


class CreateMembershipHandler(RequestHandler[CreateMembershipCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateMembershipCommand):
        if BaseRepository(Barber, self.db, tenant_id=command.tenant_id).get(command.barber_id) is None:
            raise NotFoundError("Barber not found")

        if BaseRepository(Barbershop, self.db, tenant_id=command.tenant_id).get(command.barbershop_id) is None:
            raise NotFoundError("Barbershop not found")

        if command.role not in ALLOWED_MEMBERSHIP_ROLES:
            raise ValidationError(f"Invalid role: {command.role}")

        existing = (
            self.db.query(BarbershopMembership)
            .filter(
                BarbershopMembership.barber_id == command.barber_id,
                BarbershopMembership.barbershop_id == command.barbershop_id,
                BarbershopMembership.deleted.is_(False),
            )
            .first()
        )
        if existing is not None:
            raise ConflictError("Membership already exists")

        return BaseRepository(BarbershopMembership, self.db).create(
            {
                "barber_id": command.barber_id,
                "barbershop_id": command.barbershop_id,
                "role": command.role,
                "tenant_id": command.tenant_id,
            }
        )
