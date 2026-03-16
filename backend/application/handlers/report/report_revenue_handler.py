from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.report_revenue_query import ReportRevenueQuery
from backend.core.appointment import Appointment
from backend.core.service import Service


class ReportRevenueHandler(RequestHandler[ReportRevenueQuery, dict]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ReportRevenueQuery) -> dict:
        start = datetime(
            query.start_date.year,
            query.start_date.month,
            query.start_date.day,
            tzinfo=UTC,
        )
        end = datetime(
            query.end_date.year,
            query.end_date.month,
            query.end_date.day,
            23,
            59,
            59,
            tzinfo=UTC,
        )

        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.tenant_id == query.tenant_id,
                Appointment.deleted.is_(False),
                Appointment.start_at >= start,
                Appointment.start_at <= end,
            )
            .all()
        )

        total_revenue = 0.0
        by_service: dict[int, dict] = {}

        for appt in appointments:
            service = self.db.query(Service).filter(Service.id == appt.service_id).first()
            price = service.preco if service else 0.0
            total_revenue += price
            svc_id = appt.service_id
            if svc_id not in by_service:
                by_service[svc_id] = {
                    "service_id": svc_id,
                    "service_name": service.nome if service else str(svc_id),
                    "count": 0,
                    "revenue": 0.0,
                }
            by_service[svc_id]["count"] += 1
            by_service[svc_id]["revenue"] += price

        return {
            "start_date": query.start_date.isoformat(),
            "end_date": query.end_date.isoformat(),
            "total_appointments": len(appointments),
            "total_revenue": round(total_revenue, 2),
            "by_service": list(by_service.values()),
        }
