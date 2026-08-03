"""Tests for true solar time correction."""

from datetime import datetime

from app.core.true_solar import (
    apply_true_solar_time,
    longitude_to_offset_minutes,
)


class TestTrueSolar:
    def test_zero_longitude_in_utc(self) -> None:
        assert longitude_to_offset_minutes(0.0, utc_offset_hours=0) == 0.0

    def test_east_of_reference(self) -> None:
        # Hong Kong (114°E) is 6° west of CST reference (120°E)
        # → true solar time is 24 minutes BEHIND civil time
        minutes = longitude_to_offset_minutes(114.0, utc_offset_hours=8)
        assert minutes == pytest_compatible(-24.0)

    def test_west_of_reference(self) -> None:
        minutes = longitude_to_offset_minutes(126.0, utc_offset_hours=8)
        assert minutes == pytest_compatible(24.0)

    def test_apply_returns_new_datetime(self) -> None:
        dt = datetime(2026, 8, 4, 14, 0)
        corrected = apply_true_solar_time(dt, longitude=114.0)
        assert corrected != dt


def pytest_compatible(value: float) -> float:
    return round(value, 4)
