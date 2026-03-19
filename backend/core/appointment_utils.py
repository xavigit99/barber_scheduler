from datetime import datetime

from backend.core.exceptions import ConflictError, ValidationError
from backend.core.scheduling import app_weekday_from_python, datetime_ranges_overlap


def ensure_within_availability_windows(
    availability_windows: list,
    start_at: datetime,
    end_at: datetime,
) -> None:
    start_time = start_at.time()
    end_time = end_at.time()
    weekday = app_weekday_from_python(start_at.weekday())

    for window in availability_windows:
        if window.weekday != weekday:
            continue
        if window.start_time <= start_time and end_time <= window.end_time:
            return

    raise ValidationError("Appointment falls outside barber availability")


def ensure_not_blocked(blocks: list, start_at: datetime, end_at: datetime) -> None:
    for block in blocks:
        if datetime_ranges_overlap(start_at, end_at, block.start_at, block.end_at):
            raise ConflictError("Appointment conflicts with a blocked period")
