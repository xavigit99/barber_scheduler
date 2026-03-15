from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.report_daily_query import ReportDailyQuery
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.client import Client
from backend.core.service import Service


class ReportDailyHandler(RequestHandler[ReportDailyQuery, dict]):
    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ReportDailyQuery) -> dict:
        start = datetime(
            query.target_date.year,
            query.target_date.month,
            query.target_date.day,
            tzinfo=UTC,
        )
        end = datetime(
            query.target_date.year,
            query.target_date.month,
            query.target_date.day,
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
            .order_by(Appointment.start_at)
            .all()
        )

        # Group by barber
        by_barber: dict[int, list] = {}
        for appt in appointments:
            by_barber.setdefault(appt.barber_id, []).append(appt)

        result = []
        for barber_id, appts in by_barber.items():
            barber = self.db.query(Barber).filter(Barber.id == barber_id).first()
            entries = []
            for appt in appts:
                service = self.db.query(Service).filter(Service.id == appt.service_id).first()
                client = self.db.query(Client).filter(Client.id == appt.client_id).first()
                entries.append({
                    "appointment_id": appt.id,
                    "start_at": appt.start_at,
                    "end_at": appt.end_at,
                    "service": service.nome if service else None,
                    "service_price": service.preco if service else 0,
                    "client": client.nome if client else None,
                })
            result.append({
                "barber_id": barber_id,
                "barber_name": barber.nome if barber else str(barber_id),
                "total_appointments": len(appts),
                "appointments": entries,
            })

        return {
            "date": query.target_date.isoformat(),
            "total_appointments": len(appointments),
            "barbers": result,
        }
