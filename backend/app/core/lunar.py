"""Lunar calendar conversion utilities (農曆換算) using sxtwl."""

from datetime import datetime
from typing import Any

try:
    import sxtwl  # type: ignore
    _SXTWL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SXTWL_AVAILABLE = False


def to_lunar(dt: datetime) -> dict[str, Any]:
    """Convert a solar datetime to its lunisolar representation.

    Returns a dict with the lunar year/month/day plus an ``is_leap_month`` flag.
    """
    if not _SXTWL_AVAILABLE:  # pragma: no cover
        raise RuntimeError("sxtwl is required for lunar conversion")

    day_obj = sxtwl.fromSolar(dt.year, dt.month, dt.day)

    return {
        "lunar_year": day_obj.getLunarYear(),
        "lunar_month": day_obj.getLunarMonth(),
        "lunar_day": day_obj.getLunarDay(),
        "is_leap_month": bool(day_obj.isLunarLeap()),
    }


def lunar_month_chinese(dt: datetime) -> str:
    """Return the lunar month in Chinese numerals (一..十二).

    Used as the ``cmonth`` input for kinliuren's ``Liuren`` constructor.
    """
    info = to_lunar(dt)
    chinese = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
    m = info["lunar_month"]
    if 1 <= m <= 12:
        prefix = "閏" if info["is_leap_month"] else ""
        return prefix + chinese[m]
    return chinese[m] if 0 <= m < len(chinese) else "一"
