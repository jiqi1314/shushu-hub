"""Common Pydantic schemas shared across all divination systems."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DivinationMethod = Literal["random", "datetime", "manual"]
Locale = Literal["zh-TW", "zh-CN", "en"]
Gender = Literal["male", "female"]


class GanzhiInfo(BaseModel):
    """Four Pillars (年柱、月柱、日柱、時柱) of a given moment."""

    year: str = Field(..., description="年柱, e.g. '庚午'")
    month: str = Field(..., description="月柱, e.g. '辛巳'")
    day: str = Field(..., description="日柱, e.g. '乙卯'")
    hour: str = Field(..., description="時柱, e.g. '辛未'")


class DivinationRequest(BaseModel):
    """Unified input for any divination system."""

    system: str = Field(..., description="System identifier, e.g. 'ichingshifa'")
    method: DivinationMethod = Field(..., description="How the chart is generated")

    event_at: datetime | None = Field(
        default=None,
        alias="datetime",
        description="ISO 8601 datetime; required for method=datetime",
    )
    timezone: str | None = Field(
        default=None,
        description="IANA timezone name, e.g. 'Asia/Hong_Kong'",
    )
    manual_lines: str | None = Field(
        default=None,
        min_length=6,
        max_length=6,
        description="6-char string of '6'/'7'/'8'/'9'; required for method=manual",
    )

    question: str | None = Field(default=None, description="Free-text query context")
    gender: Gender | None = Field(default=None)

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude for astrology or true solar time",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude for astrology or true solar time",
    )

    use_true_solar_time: bool = Field(
        default=False,
        description="Whether to apply longitude-based true solar time correction (opt-in, default OFF)",
    )

    locale: Locale = Field(default="zh-TW")

    model_config = {"populate_by_name": True}


class DivinationResult(BaseModel):
    """Unified output for any divination system."""

    model_config = {"arbitrary_types_allowed": True}

    system_id: str
    system_name: str
    ganzhi: GanzhiInfo | None = None
    five_elements: list[str] = Field(default_factory=list)
    main_judgment: str = ""
    favorable: list[str] = Field(default_factory=list)
    unfavorable: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    raw_output: str = ""
    computed_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    env: str
