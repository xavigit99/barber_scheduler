from datetime import datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.application.queries.get_client_segment_query import GetClientSegmentQuery
from backend.core.appointment import Appointment
from backend.core.client import Client
from backend.core.service import Service


class GetClientSegmentHandler(RequestHandler[GetClientSegmentQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetClientSegmentQuery) -> list:
        q = self.db.query(Client).filter(Client.deleted.is_(False))
        if query.tenant_id is not None:
            q = q.filter(Client.tenant_id == query.tenant_id)

        if query.inactive_days is not None:
            cutoff = datetime.now() - timedelta(days=query.inactive_days)
            active_ids = (
                self.db.query(Appointment.client_id)
                .filter(
                    Appointment.deleted.is_(False),
                    Appointment.start_at >= cutoff,
                )
                .distinct()
                .subquery()
            )
            q = q.filter(Client.id.notin_(active_ids))

        if query.min_spend is not None:
            high_spend_ids = (
                self.db.query(Appointment.client_id)
                .join(Service, Service.id == Appointment.service_id)
                .filter(Appointment.deleted.is_(False))
                .group_by(Appointment.client_id)
                .having(func.sum(Service.preco) >= query.min_spend)
                .subquery()
            )
            q = q.filter(Client.id.in_(high_spend_ids))

        if query.service_id is not None:
            svc_client_ids = (
                self.db.query(Appointment.client_id)
                .filter(
                    Appointment.deleted.is_(False),
                    Appointment.service_id == query.service_id,
                )
                .distinct()
                .subquery()
            )
            q = q.filter(Client.id.in_(svc_client_ids))

        if query.has_birthday_this_month:
            current_month = datetime.now().month
            q = q.filter(
                func.extract("month", Client.data_nascimento) == current_month,
            )

        return q.all()
