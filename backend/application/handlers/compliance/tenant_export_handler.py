from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.tenant_export_query import TenantExportQuery
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.barbershop_membership import BarbershopMembership
from backend.core.client import Client
from backend.core.service import Service


def _to_dict(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class TenantExportHandler(RequestHandler[TenantExportQuery, dict]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: TenantExportQuery) -> dict:
        tid = query.tenant_id

        barbers = self.db.query(Barber).filter(Barber.tenant_id == tid).all()
        clients = self.db.query(Client).filter(Client.tenant_id == tid).all()
        services = self.db.query(Service).filter(Service.tenant_id == tid).all()
        appointments = self.db.query(Appointment).filter(Appointment.tenant_id == tid).all()
        memberships = self.db.query(BarbershopMembership).filter(BarbershopMembership.tenant_id == tid).all()

        return {
            "tenant_id": tid,
            "exported_at": datetime.now(UTC).isoformat(),
            "barbers": [_to_dict(r) for r in barbers],
            "clients": [_to_dict(r) for r in clients],
            "services": [_to_dict(r) for r in services],
            "appointments": [_to_dict(r) for r in appointments],
            "memberships": [_to_dict(r) for r in memberships],
        }
