"""Tests for ganzhi computation."""

from datetime import datetime

import pytest

from app.core.ganzhi import compute_ganzhi


class TestGanzhi:
    def test_returns_four_pillars(self) -> None:
        result = compute_ganzhi(datetime(2026, 8, 4, 14, 30))
        assert len(result.year) == 2
        assert len(result.month) == 2
        assert len(result.day) == 2
        assert len(result.hour) == 2

    def test_valid_stems_and_branches(self) -> None:
        valid_stems = set("甲乙丙丁戊己庚辛壬癸")
        valid_branches = set("子丑寅卯辰巳午未申酉戌亥")
        result = compute_ganzhi(datetime(2026, 1, 1, 0, 0))
        for pillar in (result.year, result.month, result.day, result.hour):
            assert pillar[0] in valid_stems
            assert pillar[1] in valid_branches

    @pytest.mark.parametrize(
        "dt",
        [
            datetime(2024, 2, 10, 12, 0),
            datetime(2025, 6, 15, 23, 30),
            datetime(2026, 12, 31, 5, 45),
        ],
    )
    def test_idempotent(self, dt: datetime) -> None:
        a = compute_ganzhi(dt)
        b = compute_ganzhi(dt)
        assert a == b
