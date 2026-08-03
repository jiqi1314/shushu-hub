"""天干地支 (Heavenly Stems & Earthly Branches) computation.

Uses the proven ``sxtwl`` library which encodes the Chinese lunisolar calendar
directly. The Gan-Zhi of a given solar day/hour is purely a function of the
absolute instant in UTC, so it is timezone-independent once we have UTC.

sxtwl's ``GZ`` objects expose two independent cycle indices:
  - ``tg`` (天干 index, 0..9)
  - ``dz`` (地支 index, 0..11)
The combined ganzhi string is just ``stem[tg] + branch[dz]`` — they are NOT
components of a single 60-cycle index. (An earlier version of this file
incorrectly combined them with ``tg*12 + dz``, producing wrong pillars.)
"""

from datetime import UTC, datetime

from app.schemas.common import GanzhiInfo

try:
    import sxtwl  # type: ignore
    _SXTWL_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback path
    _SXTWL_AVAILABLE = False


_HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
_EARTHLY_BRANCHES = [
    "子", "丑", "寅", "卯", "辰", "巳",
    "午", "未", "申", "酉", "戌", "亥",
]


def _pillar(tg: int, dz: int) -> str:
    """Combine a stem index and a branch index into a 干支 string."""
    return _HEAVENLY_STEMS[tg] + _EARTHLY_BRANCHES[dz]


def _ganzhi_for_moment(dt: datetime) -> GanzhiInfo:
    """Compute the four pillars for a given UTC-aware datetime."""
    if not _SXTWL_AVAILABLE:  # pragma: no cover
        raise RuntimeError("sxtwl is required for ganzhi computation")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    dt_utc = dt.astimezone(UTC)

    day_obj = sxtwl.fromSolar(dt_utc.year, dt_utc.month, dt_utc.day)

    year_gz = day_obj.getYearGZ()
    month_gz = day_obj.getMonthGZ()
    day_gz = day_obj.getDayGZ()

    hour_branch = (dt_utc.hour + 1) // 2 % 12
    hour_stem = (day_gz.tg * 2 + hour_branch) % 10

    return GanzhiInfo(
        year=_pillar(year_gz.tg, year_gz.dz),
        month=_pillar(month_gz.tg, month_gz.dz),
        day=_pillar(day_gz.tg, day_gz.dz),
        hour=_pillar(hour_stem, hour_branch),
    )


def compute_ganzhi(dt: datetime) -> GanzhiInfo:
    """Public entry point. Accepts any timezone-aware or naive datetime."""
    return _ganzhi_for_moment(dt)