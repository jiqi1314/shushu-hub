"""Lunar calendar conversion utilities (農曆換算)."""

from datetime import datetime
from typing import Any

try:
    import sxtwl  # type: ignore
    _SXTWL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SXTWL_AVAILABLE = False


def to_lunar(dt: datetime) -> dict[str, Any]:
    """Convert a solar datetime to its lunisolar representation.

    Returns a dict with the traditional Chinese lunar fields plus the
    干支 of the day, which is the canonical input for systems like 大六壬.
    """
    if not _SXTWL_AVAILABLE:  # pragma: no cover
        raise RuntimeError("sxtwl is required for lunar conversion")

    day_obj = sxtwl.fromSolar(dt.year, dt.month, dt.day)

    return {
        "lunar_year": day_obj.getYearGZ(),
        "lunar_month": day_obj.getMonthGZ(),
        "lunar_day": day_obj.getDayGZ(),
        "is_leap_month": bool(getattr(day_obj, "isLunarLeap", False)),
    }


def solar_term_name(dt: datetime) -> str | None:
    """Return the nearest solar term name for a given moment, if available."""
    if not _SXTWL_AVAILABLE:  # pragma: no cover
        return None

    terms = ["小寒", "大寒", "立春", "雨水", "驚蟄", "春分",
             "清明", "穀雨", "立夏", "小滿", "芒種", "夏至",
             "小暑", "大暑", "立秋", "處暑", "白露", "秋分",
             "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"]

    try:
        if dt.month == 1 and dt.day <= 5:
            return "小寒" if dt.day < 3 else None
        idx = (dt.month - 1) * 2
        if idx < len(terms):
            return terms[idx]
    except Exception:
        return None
    return None
