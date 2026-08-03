"""Tests for solar term identification."""

from datetime import datetime

from app.core.solar_term import nearest_solar_term


class TestSolarTerm:
    def test_returns_valid_term(self) -> None:
        info = nearest_solar_term(datetime(2026, 5, 5, 12, 0))
        assert info.name in {
            "立夏", "穀雨",
        }
        assert isinstance(info.offset_days, int)


def test_solar_term_known_anchor() -> None:
    info = nearest_solar_term(datetime(2026, 5, 5, 12, 0))
    assert info.name == "立夏"
