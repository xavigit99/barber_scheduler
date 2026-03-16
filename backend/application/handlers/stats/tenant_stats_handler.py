from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.application.queries.tenant_stats_query import TenantStatsQuery
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.client import Client
from backend.core.service import Service


class TenantStatsHandler(RequestHandler[TenantStatsQuery, dict]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: TenantStatsQuery) -> dict:
        now = datetime.now(UTC)
        month_start = datetime(now.year, now.month, 1, tzinfo=UTC)

        barbers_count = (
            self.db.query(func.count(Barber.id))
            .filter(Barber.tenant_id == query.tenant_id, Barber.deleted.is_(False))
            .scalar()
        )

        clients_count = (
            self.db.query(func.count(Client.id))
            .filter(Client.tenant_id == query.tenant_id, Client.deleted.is_(False))
            .scalar()
        )

        services_count = (
            self.db.query(func.count(Service.id))
            .filter(Service.tenant_id == query.tenant_id, Service.deleted.is_(False))
            .scalar()
        )

        appointments_this_month = (
            self.db.query(Appointment)
            .filter(
                Appointment.tenant_id == query.tenant_id,
                Appointment.deleted.is_(False),
                Appointment.start_at >= month_start,
            )
            .all()
        )

        cancelled_this_month = (
            self.db.query(func.count(Appointment.id))
            .filter(
                Appointment.tenant_id == query.tenant_id,
                Appointment.deleted.is_(True),
                Appointment.deleted_at >= month_start,
            )
            .scalar()
        )

        revenue = 0.0
        for appt in appointments_this_month:
            service = self.db.query(Service).filter(Service.id == appt.service_id).first()
            if service:
                revenue += service.preco

        return {
            "barbers": barbers_count or 0,
            "clients": clients_count or 0,
            "services": services_count or 0,
            "appointments_month": len(appointments_this_month),
            "cancelled_month": cancelled_this_month or 0,
            "revenue_month": revenue,
        }
