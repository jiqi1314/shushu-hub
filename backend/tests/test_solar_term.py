"""Tests for solar term identification.

Reference dates (2026) verified against sxtwl's getJieQi output:
  小寒 1/5, 大寒 1/20, 立春 2/4, 雨水 2/18, 驚蟄 3/5, 春分 3/20,
  清明 4/5, 穀雨 4/20, 立夏 5/5, 小滿 5/21, 芒種 6/5, 夏至 6/21,
  小暑 7/7, 大暑 7/23, 立秋 8/7, 處暑 8/23, 白露 9/7, 秋分 9/23,
  寒露 10/8, 霜降 10/23, 立冬 11/7, 小雪 11/22, 大雪 12/7, 冬至 12/22.
"""

from datetime import datetime

import pytest

from app.core.solar_term import (
    current_solar_term,
    nearest_solar_term,
    next_solar_term,
)


# (date, expected current term) — dates just AFTER the term, so the
# term has clearly already occurred and is the unambiguous answer.
KNOWN_DATES = [
    (datetime(2026, 1, 6),  "小寒"),   # 小寒 1/5 翌日
    (datetime(2026, 1, 20), "大寒"),   # 大寒當天
    (datetime(2026, 1, 21), "大寒"),   # 大寒翌日
    (datetime(2026, 2, 4),  "立春"),   # 立春當天
    (datetime(2026, 2, 18), "雨水"),
    (datetime(2026, 3, 5),  "驚蟄"),
    (datetime(2026, 3, 20), "春分"),
    (datetime(2026, 4, 5),  "清明"),
    (datetime(2026, 4, 20), "穀雨"),
    (datetime(2026, 5, 5),  "立夏"),
    (datetime(2026, 5, 21), "小滿"),
    (datetime(2026, 6, 5),  "芒種"),
    (datetime(2026, 6, 21), "夏至"),
    (datetime(2026, 7, 7),  "小暑"),
    (datetime(2026, 7, 23), "大暑"),   # 大暑 2026 落在 7/23，不是 22
    (datetime(2026, 8, 4),  "大暑"),   # 大暑後、立秋前 ← 之前錯誤回傳夏至
    (datetime(2026, 8, 7),  "立秋"),
    (datetime(2026, 8, 23), "處暑"),
    (datetime(2026, 9, 7),  "白露"),
    (datetime(2026, 9, 23), "秋分"),
    (datetime(2026, 10, 8),  "寒露"),
    (datetime(2026, 10, 23), "霜降"),
    (datetime(2026, 11, 7),  "立冬"),
    (datetime(2026, 11, 22), "小雪"),
    (datetime(2026, 12, 7),  "大雪"),
    (datetime(2026, 12, 22), "冬至"),   # 冬至 2026 落在 12/22，不是 21
]


class TestSolarTerm:
    def test_returns_valid_term(self) -> None:
        info = nearest_solar_term(datetime(2026, 5, 5, 12, 0))
        assert info.name in {"立夏", "穀雨"}
        assert isinstance(info.offset_days, int)

    @pytest.mark.parametrize(
        "dt,expected",
        KNOWN_DATES,
        ids=[f"{dt.strftime('%Y-%m-%d')}" for dt, _ in KNOWN_DATES],
    )
    def test_current_solar_term(self, dt: datetime, expected: str) -> None:
        actual = current_solar_term(dt)
        assert actual == expected, (
            f"{dt.date()} should be in {expected}, got {actual}"
        )


def test_solar_term_known_anchor() -> None:
    info = nearest_solar_term(datetime(2026, 5, 5, 12, 0))
    assert info.name == "立夏"


def test_next_solar_term_after_date() -> None:
    name, days = next_solar_term(datetime(2026, 8, 4))
    assert name == "立秋"
    assert days == 3  # 8/7 - 8/4 = 3 days
