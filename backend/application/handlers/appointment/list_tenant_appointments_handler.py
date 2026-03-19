from datetime import datetime, time, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_tenant_appointments_query import (
    ListTenantAppointmentsQuery,
)
from backend.core.appointment import Appointment


class ListTenantAppointmentsHandler(
    RequestHandler[ListTenantAppointmentsQuery, list]
):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListTenantAppointmentsQuery) -> list:
        appointment_query = self.db.query(Appointment).filter(
            Appointment.tenant_id == query.tenant_id,
            Appointment.deleted.is_(False),
        )

        if query.barber_id is not None:
            appointment_query = appointment_query.filter(
                Appointment.barber_id == query.barber_id,
            )

        if query.target_date:
            day_start = datetime.combine(query.target_date, time.min)
            day_end = day_start + timedelta(days=1)
            appointment_query = appointment_query.filter(
                Appointment.start_at >= day_start,
                Appointment.start_at < day_end,
            )

        return appointment_query.order_by(Appointment.start_at).all()
