from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.core.exceptions import ConflictError, ValidationError

BREAK_BLOCK_KIND = "break"
DAY_OFF_BLOCK_KIND = "day_off"
MANUAL_BLOCK_KIND = "block"

ALLOWED_BLOCK_KINDS = {
    BREAK_BLOCK_KIND,
    DAY_OFF_BLOCK_KIND,
    MANUAL_BLOCK_KIND,
}

SLOT_INTERVAL_MINUTES = 15


def app_weekday_from_python(weekday: int) -> int:
    return (weekday + 1) % 7


def validate_weekday(weekday: int) -> None:
    if weekday < 0 or weekday > 6:
        raise ValidationError("weekday must be between 0 and 6")


def validate_time_range(start_time: time, end_time: time) -> None:
    if start_time >= end_time:
        raise ValidationError("start_time must be earlier than end_time")


def validate_datetime_range(start_at: datetime, end_at: datetime) -> None:
    if start_at >= end_at:
        raise ValidationError("start_at must be earlier than end_at")


def validate_block_kind(kind: str) -> None:
    if kind not in ALLOWED_BLOCK_KINDS:
        raise ValidationError("Invalid block type")


def ensure_valid_timezone(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValidationError("Invalid timezone") from exc


def time_ranges_overlap(
    start_a: time,
    end_a: time,
    start_b: time,
    end_b: time,
) -> bool:
    return start_a < end_b and start_b < end_a


def datetime_ranges_overlap(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime,
) -> bool:
    return start_a < end_b and start_b < end_a


def ensure_no_availability_overlap(
    existing_availabilities: list,
    *,
    weekday: int,
    start_time: time,
    end_time: time,
    exclude_availability_id: int | None = None,
) -> None:
    for availability in existing_availabilities:
        if availability.weekday != weekday:
            continue
        if exclude_availability_id is not None and availability.id == exclude_availability_id:
            continue
        if time_ranges_overlap(
            start_time,
            end_time,
            availability.start_time,
            availability.end_time,
        ):
            raise ConflictError("Availability window overlaps an existing window")


def normalize_local_datetime(value: datetime, timezone: ZoneInfo) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone)
    return value.astimezone(timezone)


def build_daily_slots(
    *,
    target_date: date,
    timezone_name: str,
    availability_windows: list,
    blocks: list,
    service_duration_minutes: int,
    earliest_start_at: datetime | None = None,
) -> list[dict]:
    timezone = ensure_valid_timezone(timezone_name)
    slot_duration = timedelta(minutes=service_duration_minutes)
    slot_interval = timedelta(minutes=SLOT_INTERVAL_MINUTES)
    slots: list[dict] = []
    earliest_local = (
        normalize_local_datetime(earliest_start_at, timezone)
        if earliest_start_at is not None
        else None
    )
    target_weekday = app_weekday_from_python(target_date.weekday())

    for availability in availability_windows:
        if availability.weekday != target_weekday:
            continue

        window_start = datetime.combine(target_date, availability.start_time, tzinfo=timezone)
        window_end = datetime.combine(target_date, availability.end_time, tzinfo=timezone)
        cursor = window_start

        while cursor + slot_duration <= window_end:
            candidate_end = cursor + slot_duration
            overlaps_block = False

            if earliest_local is not None and cursor <= earliest_local:
                cursor += slot_interval
                continue

            for block in blocks:
                block_start = normalize_local_datetime(block.start_at, timezone)
                block_end = normalize_local_datetime(block.end_at, timezone)
                if datetime_ranges_overlap(cursor, candidate_end, block_start, block_end):
                    overlaps_block = True
                    break

            if not overlaps_block:
                slots.append(
                    {
                        "inicio": cursor,
                        "fim": candidate_end,
                    }
                )

            cursor += slot_interval

    return slots
