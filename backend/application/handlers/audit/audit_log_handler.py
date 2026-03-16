from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.audit_log_query import AuditLogQuery
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


class AuditLogHandler(RequestHandler[AuditLogQuery, list]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: AuditLogQuery) -> list:
        model = _ENTITY_MAP.get(query.entity.lower())
        if model is None:
            raise ValueError(f"Unknown entity: {query.entity}")

        q = self.db.query(model).filter(
            model.tenant_id == query.tenant_id,
            model.deleted.is_(True),
        )

        if query.from_date is not None:
            q = q.filter(model.deleted_at >= datetime(query.from_date.year, query.from_date.month, query.from_date.day))

        if query.to_date is not None:
            q = q.filter(model.deleted_at < datetime(query.to_date.year, query.to_date.month, query.to_date.day + 1))

        records = q.all()

        result = []
        for rec in records:
            entry = {"id": rec.id, "deleted_at": rec.deleted_at}
            for field in ("nome", "email", "start_at", "end_at", "role"):
                if hasattr(rec, field):
                    entry[field] = getattr(rec, field)
            result.append(entry)

        return result
