from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from backend.core.appointment import Appointment
from backend.core.barber import Barber
from backend.core.barber_availability import BarberAvailability
from backend.core.barber_block import BarberBlock
from backend.core.exceptions import NotFoundError
from backend.core.scheduling import build_daily_slots, normalize_local_datetime
from backend.core.service import Service
from repositories.base_repository import BaseRepository


def get_available_slots_payload(
    db: Session,
    *,
    barber_id: int,
    service_id: int,
    target_date,
    timezone: str,
) -> dict:
    barber_repository = BaseRepository(Barber, db)
    service_repository = BaseRepository(Service, db)

    if barber_repository.get(barber_id) is None:
        raise NotFoundError("Barber not found")

    service = service_repository.get(service_id)
    if service is None:
        raise NotFoundError("Service not found")

    timezone_info = ZoneInfo(timezone)
    availability_windows = (
        db.query(BarberAvailability)
        .filter(
            BarberAvailability.barber_id == barber_id,
            BarberAvailability.deleted.is_(False),
        )
        .order_by(BarberAvailability.start_time)
        .all()
    )

    day_start = datetime.combine(target_date, time.min, tzinfo=timezone_info)
    day_end = day_start + timedelta(days=1)

    raw_blocks = (
        db.query(BarberBlock)
        .filter(
            BarberBlock.barber_id == barber_id,
            BarberBlock.deleted.is_(False),
        )
        .order_by(BarberBlock.start_at)
        .all()
    )
    blocks = [
        block for block in raw_blocks
        if normalize_local_datetime(block.start_at, timezone_info) < day_end
        and normalize_local_datetime(block.end_at, timezone_info) > day_start
    ]

    raw_existing_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.barber_id == barber_id,
            Appointment.deleted.is_(False),
        )
        .all()
    )
    existing_appointments = [
        appointment for appointment in raw_existing_appointments
        if normalize_local_datetime(appointment.start_at, timezone_info) < day_end
        and normalize_local_datetime(appointment.end_at, timezone_info) > day_start
    ]

    class _AppointmentBlock:
        def __init__(self, appointment: Appointment):
            self.start_at = appointment.start_at
            self.end_at = appointment.end_at

    all_blocks = list(blocks) + [_AppointmentBlock(appointment) for appointment in existing_appointments]
    now_local = datetime.now(timezone_info)
    earliest_start_at = now_local if target_date == now_local.date() else None

    return {
        "barber_id": barber_id,
        "service_id": service_id,
        "data": target_date,
        "timezone": timezone,
        "slots": build_daily_slots(
            target_date=target_date,
            timezone_name=timezone,
            availability_windows=availability_windows,
            blocks=all_blocks,
            service_duration_minutes=service.duracao_minutos,
            earliest_start_at=earliest_start_at,
        ),
    }
