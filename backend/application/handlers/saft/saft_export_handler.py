from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.saft_export_query import SaftExportQuery
from backend.core.appointment import Appointment
from backend.core.service import Service


class SaftExportHandler(RequestHandler[SaftExportQuery, dict]):
    """Aggregates appointment data for SAF-T-PT stub export (F36)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: SaftExportQuery) -> dict:
        year_start = datetime(query.year, 1, 1, tzinfo=UTC)
        year_end = datetime(query.year + 1, 1, 1, tzinfo=UTC)

        appointments = (
            self.db.query(Appointment)
            .filter(
                Appointment.tenant_id == query.tenant_id,
                Appointment.deleted.is_(False),
                Appointment.start_at >= year_start,
                Appointment.start_at < year_end,
            )
            .all()
        )

        # Aggregate revenue per service
        service_map: dict[int, dict] = {}
        total_revenue = 0.0

        for appt in appointments:
            sid = appt.service_id
            if sid not in service_map:
                service = self.db.query(Service).filter(Service.id == sid).first()
                service_map[sid] = {
                    "service_id": sid,
                    "nome": service.nome if service else "Desconhecido",
                    "count": 0,
                    "revenue": 0.0,
                    "preco": service.preco if service else 0.0,
                }
            service_map[sid]["count"] += 1
            service_map[sid]["revenue"] += service_map[sid]["preco"]
            total_revenue += service_map[sid]["preco"]

        # Remove the helper field before returning
        services = [
            {k: v for k, v in entry.items() if k != "preco"}
            for entry in service_map.values()
        ]

        return {
            "year": query.year,
            "tenant_id": query.tenant_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "appointments_count": len(appointments),
            "total_revenue": round(total_revenue, 2),
            "services": services,
        }
