"""Common Pydantic schemas shared across all divination systems."""

from datetime import datetime
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

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

    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-system knobs (e.g. qimen variant='chabu'|'zhirun')",
    )

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


class CompareRequest(BaseModel):
    """Request body for ``POST /api/compare``.

    Either specify explicit ``systems``, or omit to run all currently
    registered modules. Common fields (``event_at``, ``timezone``, etc.)
    are shared across all systems; per-system knobs go in ``per_system``.
    """

    systems: list[str] | None = Field(
        default=None,
        description=(
            "List of system IDs to run (e.g. ['ichingshifa','liuren']). "
            "If null, run all registered modules."
        ),
    )
    method: DivinationMethod = Field(default="datetime")
    event_at: datetime | None = Field(
        default=None, alias="datetime", description="ISO 8601 datetime"
    )
    timezone: str | None = Field(default=None, description="IANA timezone")
    manual_lines: str | None = Field(
        default=None, min_length=6, max_length=6, description="For ichingshifa manual"
    )
    question: str | None = Field(default=None)
    gender: Gender | None = Field(default=None)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    use_true_solar_time: bool = Field(default=False)
    locale: Locale = Field(default="zh-TW")

    per_system: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Per-system overrides, keyed by system_id. Example: "
            "{'qimen': {'variant': 'zhirun'}, 'taiyi': {'scope': 'nianji'}}"
        ),
    )

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def _validate_method_support(self) -> Self:
        if self.systems is not None:
            invalid_method_systems = {"liuren", "qimen", "taiyi"}
            if self.method != "datetime" and any(
                s in invalid_method_systems for s in self.systems
            ):
                raise ValueError(
                    "Only ichingshifa supports method=random/manual; "
                    "other systems require method=datetime."
                )
        return self


class SystemFailure(BaseModel):
    """Per-system failure reported in CompareResponse.failures."""

    system: str
    error_code: str
    message: str


class CompareResponse(BaseModel):
    """Response for ``POST /api/compare``.

    Includes each successful system's full result plus a cross-system
    analysis derived by ``field_mapper``. Individual failures are listed
    separately so the rest of the comparison can still be shown.
    """

    results: list[DivinationResult]
    cross_analysis: dict[str, Any] = Field(default_factory=dict)
    failures: list[SystemFailure] = Field(default_factory=list)
    question: str | None = None
    computed_at: datetime = Field(default_factory=lambda: datetime.utcnow())
