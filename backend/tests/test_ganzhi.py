"""Tests for ganzhi computation.

These tests pin the implementation against known ground-truth values that
have been independently verified (e.g. via 万年曆查表 or kinqimen/kinliuren
output). Adding a wrong assertion here is worse than not having it — the
goal is to catch the exact ``tg*12+dz`` bug that corrupted all four
pillars in the first version of this module.
"""

from datetime import datetime

import pytest

from app.core.ganzhi import compute_ganzhi


# (year, month, day, hour, minute) → expected (年, 月, 日, 時)
# All values cross-checked with sxtwl.fromSolar().getYearGZ/MonthGZ/DayGZ
# and confirmed against the kentang2017 upstream libraries' output.
REFERENCE_DATES = [
    (
        datetime(2026, 8, 4, 14, 30),
        ("丙午", "乙未", "庚戌", "癸未"),
        "user-verified: 庚戌日 / 乙未月 / 丙午年",
    ),
    (
        datetime(2026, 5, 15, 14, 30),
        ("丙午", "癸巳", "己丑", "辛未"),
        "kinqimen output: 丙午年癸巳月己丑日辛未時",
    ),
    (
        datetime(2026, 1, 1, 0, 0),
        ("乙巳", "戊子", "乙亥", "丙子"),
        "sxtwl verified: 2026 starts before 立春 → previous year 乙巳",
    ),
    (
        datetime(2024, 2, 10, 12, 0),
        ("甲辰", "丙寅", "甲辰", "庚午"),
        "甲辰 year (2024 leap year edge case)",
    ),
    (
        datetime(2025, 6, 15, 23, 30),
        ("乙巳", "壬午", "乙卯", "丙子"),
        "late-evening edge case (23:30 = 子時 next day borderline)",
    ),
    (
        datetime(2026, 12, 31, 5, 45),
        ("丙午", "庚子", "己卯", "丁卯"),
        "year-end edge case (5:45 = 卯時)",
    ),
    (
        datetime(2020, 1, 1, 0, 0),
        ("己亥", "丙子", "癸卯", "壬子"),
        "regression: 2020 = 己亥年 (Rat year)",
    ),
]


class TestGanzhiShape:
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
            assert pillar[0] in valid_stems, f"bad stem in {pillar}"
            assert pillar[1] in valid_branches, f"bad branch in {pillar}"


class TestGanzhiAgainstReference:
    """Ground-truth regression suite.

    These exact-value assertions are the only thing that would have caught
    the original ``_stem_branch(tg*12 + dz)`` bug, which produced plausible
    but wrong pillars for every datetime.
    """

    @pytest.mark.parametrize(
        "dt,expected,label",
        REFERENCE_DATES,
        ids=[f"{dt.strftime('%Y-%m-%d %H:%M')}" for dt, *_ in REFERENCE_DATES],
    )
    def test_matches_reference(self, dt: datetime, expected: tuple, label: str) -> None:
        result = compute_ganzhi(dt)
        actual = (result.year, result.month, result.day, result.hour)
        assert actual == expected, (
            f"{label}\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}\n"
            f"  (this regression was the original tg*12+dz bug)"
        )


class TestGanzhiHourBranch:
    """Verify the (hour+1)//2 % 12 hour-branch mapping."""

    @pytest.mark.parametrize(
        "hour,expected_branch",
        [
            (0, "子"), (1, "丑"), (2, "丑"), (3, "寅"),
            (4, "寅"), (5, "卯"), (6, "卯"), (7, "辰"),
            (8, "辰"), (9, "巳"), (10, "巳"), (11, "午"),
            (12, "午"), (13, "未"), (14, "未"), (15, "申"),
            (16, "申"), (17, "酉"), (18, "酉"), (19, "戌"),
            (20, "戌"), (21, "亥"), (22, "亥"), (23, "子"),
        ],
    )
    def test_hour_branch_mapping(self, hour: int, expected_branch: str) -> None:
        result = compute_ganzhi(datetime(2026, 8, 4, hour, 0))
        assert result.hour[1] == expected_branch, (
            f"hour={hour} should map to branch {expected_branch}, "
            f"got {result.hour}"
        )


class TestGanzhiIdempotent:
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