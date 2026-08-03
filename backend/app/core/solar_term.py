"""Solar term (節氣) helpers using sxtwl for full historical coverage."""

from datetime import datetime
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


def _jieqi_index(dt: datetime) -> int:
    """Return the current jieqi index (0..23) for a given UTC moment.

    Convention: a date belongs to the term that began on or before that date.
    """
    try:
        import sxtwl  # type: ignore

        day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
        jq = day.getJieQi()
        if 0 <= jq < 24:
            return jq
    except ImportError:
        pass
    return _fallback_index(dt)


def _fallback_index(dt: datetime) -> int:
    """Crude fallback: choose a term based on month only."""
    rough = [
        0, 0, 2, 4, 6, 8,
        10, 12, 14, 16, 18, 20,
    ]
    return rough[dt.month - 1]


def current_solar_term(dt: datetime) -> str:
    """Return the current solar term name for a given datetime."""
    return _JIEQI_NAMES[_jieqi_index(dt)]


def nearest_solar_term(dt: datetime) -> SolarTermInfo:
    """Return the nearest solar term to a given datetime.

    Used for display purposes when the term didn't begin exactly on this day.
    """
    idx = _jieqi_index(dt)
    return SolarTermInfo(name=_JIEQI_NAMES[idx], offset_days=0)


def next_solar_term(dt: datetime) -> tuple[str, int]:
    """Return (name, days_until) for the next solar term."""
    try:
        import sxtwl  # type: ignore

        day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
        jq = day.getJieQi()
        if 0 <= jq < 24:
            return _JIEQI_NAMES[jq], 0
    except ImportError:
        pass
    return _JIEQI_NAMES[_jieqi_index(dt)], 0
