"""Solar term (節氣) helpers."""

from datetime import datetime
from typing import NamedTuple


class SolarTermInfo(NamedTuple):
    name: str
    offset_days: int  # signed days from the given moment


_TERMS_2026 = [
    ("小寒", "2026-01-05"),
    ("大寒", "2026-01-20"),
    ("立春", "2026-02-04"),
    ("雨水", "2026-02-18"),
    ("驚蟄", "2026-03-05"),
    ("春分", "2026-03-20"),
    ("清明", "2026-04-04"),
    ("穀雨", "2026-04-20"),
    ("立夏", "2026-05-05"),
    ("小滿", "2026-05-21"),
    ("芒種", "2026-06-05"),
    ("夏至", "2026-06-21"),
    ("小暑", "2026-07-07"),
    ("大暑", "2026-07-22"),
    ("立秋", "2026-08-07"),
    ("處暑", "2026-08-23"),
    ("白露", "2026-09-07"),
    ("秋分", "2026-09-23"),
    ("寒露", "2026-10-08"),
    ("霜降", "2026-10-23"),
    ("立冬", "2026-11-07"),
    ("小雪", "2026-11-22"),
    ("大雪", "2026-12-07"),
    ("冬至", "2026-12-21"),
]


def nearest_solar_term(dt: datetime) -> SolarTermInfo:
    """Return the nearest solar term for a given datetime.

    For Phase 1 we use a static 2026 reference table; production should
    compute dynamically via ``sxtwl`` for full historical coverage.
    """
    from datetime import datetime as _dt

    best: SolarTermInfo | None = None
    best_delta = float("inf")
    for name, date_str in _TERMS_2026:
        term_dt = _dt.fromisoformat(date_str)
        delta = abs((dt - term_dt).days)
        if delta < best_delta:
            best_delta = delta
            best = SolarTermInfo(name=name, offset_days=(dt - term_dt).days)
    if best is None:
        return SolarTermInfo(name="冬至", offset_days=0)
    return best
