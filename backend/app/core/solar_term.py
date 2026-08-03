"""Solar term (節氣) helpers using sxtwl for full historical coverage."""

from datetime import datetime, timedelta
from typing import NamedTuple


class SolarTermInfo(NamedTuple):
    name: str
    offset_days: int


_JIEQI_NAMES = [
    "冬至", "小寒", "大寒", "立春", "雨水", "驚蟄",
    "春分", "清明", "穀雨", "立夏", "小滿", "芒種",
    "夏至", "小暑", "大暑", "立秋", "處暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
]


def _current_jieqi_index(dt: datetime) -> tuple[int, int]:
    """Return ``(jieqi_index, days_since)`` for the most recent solar term.

    Convention: the \"current\" 節氣 is the most recent one that occurred
    *on or before* ``dt``. Days since is 0 if the term fell on ``dt`` itself.

    sxtwl's ``Day.getJieQi()`` returns the index only when a term falls on
    that exact solar day; otherwise it returns 255 (a sentinel). We walk
    backward up to 30 days to find the most recent term.
    """
    try:
        import sxtwl  # type: ignore
    except ImportError:
        return _fallback(dt), 0

    cur_date = dt.date()
    for offset in range(31):
        candidate = cur_date - timedelta(days=offset)
        day_obj = sxtwl.fromSolar(candidate.year, candidate.month, candidate.day)
        jq = day_obj.getJieQi()
        if 0 <= jq < 24:
            return jq, offset
    return _fallback(dt), 0


def _fallback(dt: datetime) -> int:
    """Crude fallback: pick a jieqi index based on the month only."""
    rough = [
        0, 0, 2, 4, 6, 8,
        10, 12, 14, 16, 18, 20,
    ]
    return rough[dt.month - 1]


def current_solar_term(dt: datetime) -> str:
    """Return the current solar term name (the most recent one on or before dt)."""
    idx, _ = _current_jieqi_index(dt)
    return _JIEQI_NAMES[idx]


def nearest_solar_term(dt: datetime) -> SolarTermInfo:
    """Return the nearest solar term (most recent on or before dt)."""
    idx, offset = _current_jieqi_index(dt)
    return SolarTermInfo(name=_JIEQI_NAMES[idx], offset_days=-offset)


def next_solar_term(dt: datetime) -> tuple[str, int]:
    """Return ``(name, days_until)`` for the next solar term strictly after dt."""
    try:
        import sxtwl  # type: ignore
    except ImportError:
        idx, _ = _current_jieqi_index(dt)
        return _JIEQI_NAMES[(idx + 1) % 24], 0

    cur_date = dt.date()
    for offset in range(1, 32):
        candidate = cur_date + timedelta(days=offset)
        day_obj = sxtwl.fromSolar(candidate.year, candidate.month, candidate.day)
        jq = day_obj.getJieQi()
        if 0 <= jq < 24:
            return _JIEQI_NAMES[jq], offset
    return _JIEQI_NAMES[0], 0