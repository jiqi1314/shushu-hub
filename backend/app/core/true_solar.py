"""True solar time (真太陽時) correction utilities.

True solar time correction is **opt-in** only. The default behavior across
``shushu-hub`` is to use the user's declared civil time without correction,
which matches the conservative practice of most traditional 命理 workflows.

The correction is purely a function of longitude (4 minutes per degree east
of the timezone reference meridian). We deliberately ignore the equation
of time; the additional few-second wobble is negligible for divination
purposes and would only complicate reproducibility.
"""

from datetime import datetime, timedelta

# Reference meridians (in degrees east) for common UTC offsets.
_TIMEZONE_REFERENCE_MERIDIANS: dict[int, float] = {
    0: 0.0,        # UTC
    1: 15.0,       # CET
    8: 120.0,      # CST (China Standard Time)
    9: 135.0,      # JST
    -5: -75.0,     # EST
    -8: -120.0,    # PST
}


def longitude_to_offset_minutes(longitude: float, utc_offset_hours: int) -> float:
    """Return the minutes to add to civil time to get true solar time.

    4 minutes per degree east of the timezone's reference meridian.
    """
    ref = _TIMEZONE_REFERENCE_MERIDIANS.get(utc_offset_hours, utc_offset_hours * 15.0)
    diff_deg = longitude - ref
    return diff_deg * 4.0


def apply_true_solar_time(dt: datetime, longitude: float) -> datetime:
    """Apply longitude-based true solar time correction.

    The caller MUST have already verified ``use_true_solar_time`` is True
    and that ``longitude`` is provided.
    """
    offset_minutes = longitude_to_offset_minutes(longitude, _utc_offset_hours(dt))
    return dt + timedelta(minutes=offset_minutes)


def _utc_offset_hours(dt: datetime) -> int:
    """Return the UTC offset of ``dt`` in whole hours.

    For non-aware datetimes, assume 0. For aware datetimes, use the offset.
    """
    if dt.tzinfo is None:
        return 0
    offset = dt.utcoffset()
    if offset is None:
        return 0
    return int(offset.total_seconds() // 3600)
