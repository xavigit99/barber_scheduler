from datetime import UTC, datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.purge_deleted_command import PurgeDeletedCommand
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.barbershop import Barbershop
from backend.core.barbershop_membership import BarbershopMembership
from backend.core.client import Client
from backend.core.service import Service

_ENTITY_MAP = {
    "barber": Barber,
    "client": Client,
    "service": Service,
    "appointment": Appointment,
    "barbershop": Barbershop,
    "membership": BarbershopMembership,
}


class PurgeDeletedHandler(RequestHandler[PurgeDeletedCommand, dict]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: PurgeDeletedCommand) -> dict:
        model = _ENTITY_MAP.get(command.entity.lower())
        if model is None:
            raise ValueError(f"Unknown entity: {command.entity}")

        cutoff = datetime.now(UTC) - timedelta(days=command.older_than_days)

        records = (
            self.db.query(model)
            .filter(
                model.tenant_id == command.tenant_id,
                model.deleted.is_(True),
                model.deleted_at < cutoff,
            )
            .all()
        )

        count = len(records)
        for rec in records:
            self.db.delete(rec)

        if count:
            self.db.commit()

        return {"entity": command.entity, "purged_count": count}
