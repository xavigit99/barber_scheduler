from datetime import datetime, time, timedelta

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_barber_appointments_query import (
    ListBarberAppointmentsQuery,
)
from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.exceptions import NotFoundError
from repositories.base_repository import BaseRepository


class ListBarberAppointmentsHandler(
    RequestHandler[ListBarberAppointmentsQuery, list]
):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListBarberAppointmentsQuery) -> list:
        barber_repository = BaseRepository(Barber, self.db, query.tenant_id)
        if barber_repository.get(query.barber_id) is None:
            raise NotFoundError("Barber not found")

        appointment_query = self.db.query(Appointment).filter(
            Appointment.barber_id == query.barber_id,
            Appointment.deleted.is_(False),
        )

        if query.target_date:
            day_start = datetime.combine(query.target_date, time.min)
            day_end = day_start + timedelta(days=1)
            appointment_query = appointment_query.filter(
                Appointment.start_at >= day_start,
                Appointment.start_at < day_end,
            )

        return appointment_query.order_by(Appointment.start_at).all()
