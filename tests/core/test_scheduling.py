import os
import unittest
from datetime import date, datetime, time
from types import SimpleNamespace

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.core.exceptions import ConflictError, ValidationError
from backend.core.scheduling import (
    build_daily_slots,
    ensure_no_availability_overlap,
    ensure_valid_timezone,
    validate_time_range,
)


class SchedulingTestCase(unittest.TestCase):

    def test_ensure_no_availability_overlap_rejects_intersection(self):
        existing = [
            SimpleNamespace(
                id=1,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(12, 0),
            )
        ]

        with self.assertRaises(ConflictError) as context:
            ensure_no_availability_overlap(
                existing,
                weekday=0,
                start_time=time(11, 0),
                end_time=time(13, 0),
            )

        self.assertEqual(str(context.exception), "Availability window overlaps an existing window")

    def test_build_daily_slots_respects_blocked_ranges(self):
        slots = build_daily_slots(
            target_date=date(2026, 3, 16),
            timezone_name="Europe/Lisbon",
            availability_windows=[
                SimpleNamespace(
                    weekday=0,
                    start_time=time(9, 0),
                    end_time=time(11, 0),
                )
            ],
            blocks=[
                SimpleNamespace(
                    start_at=datetime(2026, 3, 16, 10, 0),
                    end_at=datetime(2026, 3, 16, 10, 30),
                )
            ],
            service_duration_minutes=30,
        )

        self.assertEqual(len(slots), 4)
        self.assertEqual(slots[0]["inicio"].hour, 9)
        self.assertEqual(slots[-1]["inicio"].hour, 10)
        self.assertEqual(slots[-1]["inicio"].minute, 30)

    def test_ensure_valid_timezone_rejects_invalid_value(self):
        with self.assertRaises(ValidationError) as context:
            ensure_valid_timezone("Mars/Olympus")

        self.assertEqual(str(context.exception), "Invalid timezone")

    def test_validate_time_range_rejects_inverted_window(self):
        with self.assertRaises(ValidationError) as context:
            validate_time_range(time(18, 0), time(9, 0))

        self.assertEqual(str(context.exception), "start_time must be earlier than end_time")


if __name__ == "__main__":
    unittest.main()
