"""天干地支 (Heavenly Stems & Earthly Branches) computation.

Uses the proven ``sxtwl`` library which encodes the Chinese lunisolar calendar
directly. The Gan-Zhi of a given solar day/hour is purely a function of the
absolute instant in UTC, so it is timezone-independent once we have UTC.
"""

from datetime import UTC, datetime

from app.schemas.common import GanzhiInfo

try:
    import sxtwl  # type: ignore
    _SXTWL_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback path
    _SXTWL_AVAILABLE = False


_HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
_EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _stem_branch(idx: int) -> str:
    """Return ``天干地支`` combined string for a 60-cycle index (0..59)."""
    return _HEAVENLY_STEMS[idx % 10] + _EARTHLY_BRANCHES[idx % 12]


def _ganzhi_for_moment(dt: datetime) -> GanzhiInfo:
    """Compute the four pillars for a given UTC-aware datetime.

    ``sxtwl.fromSolar(year, month, day)`` returns the lunar day index where
    day stem/branch are stored. Hour pillar is derived from the same day's
    hour stem/branch tables.
    """
    if not _SXTWL_AVAILABLE:  # pragma: no cover
        raise RuntimeError("sxtwl is required for ganzhi computation")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    dt_utc = dt.astimezone(UTC)

    day_obj = sxtwl.fromSolar(dt_utc.year, dt_utc.month, dt_utc.day)

    year_idx = day_obj.getYearGZ()
    month_idx = day_obj.getMonthGZ()
    day_idx = day_obj.getDayGZ()

    hour_branch = (dt_utc.hour + 1) // 2 % 12
    day_stem = day_idx.tg
    hour_stem = (day_stem * 2 + hour_branch) % 10
    hour_idx = (hour_stem, hour_branch)

    return GanzhiInfo(
        year=_stem_branch(year_idx.tg * 12 + year_idx.dz),
        month=_stem_branch(month_idx.tg * 12 + month_idx.dz),
        day=_stem_branch(day_idx.tg * 12 + day_idx.dz),
        hour=_stem_branch(hour_idx[0] * 12 + hour_idx[1]),
    )


def compute_ganzhi(dt: datetime) -> GanzhiInfo:
    """Public entry point. Accepts any timezone-aware or naive datetime."""
    return _ganzhi_for_moment(dt)
