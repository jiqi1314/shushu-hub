"""大六壬 (Da Liu Ren) adapter.

Wraps the upstream ``kinliuren`` library. The upstream ``Liuren`` constructor
requires four pre-computed Chinese calendar inputs:

  - ``jieqi``         : 當前節氣, e.g. "驚蟄"
  - ``cmonth``        : 農曆月份 (中文數字), e.g. "二" or "閏二"
  - ``daygangzhi``    : 日柱干支, e.g. "己未"
  - ``hourgangzhi``   : 時柱干支, e.g. "甲午"

We derive all four from a single ISO 8601 ``datetime`` via the core helpers
in ``app.core``. The result dict is normalized into our ``DivinationResult``
schema, with the most decision-relevant fields (三傳、四課、格局、神煞)
preserved under ``details``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core import (
    compute_ganzhi,
    current_solar_term,
    lunar_month_chinese,
)
from app.modules.base import BaseModule
from app.schemas.common import DivinationRequest, DivinationResult, GanzhiInfo


class LiuRenModule(BaseModule):
    """Adapter for kentang2017/kinliuren."""

    system_id = "liuren"
    system_name = "大六壬"
    description = "三式之首，四課三傳、天地盤、神煞格局 (Da Liu Ren)"

    def __init__(self) -> None:
        try:
            from kinliuren import kinliuren  # type: ignore

            self._Liuren = kinliuren.Liuren
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise RuntimeError(
                "kinliuren package is required: pip install kinliuren"
            ) from exc

    def validate(self, request: DivinationRequest) -> None:
        if request.method == "manual":
            raise ValueError("大六壬 does not support manual method; use datetime")
        if request.event_at is None:
            raise ValueError("event_at (datetime) is required for 大六壬")

    def compute(self, request: DivinationRequest) -> DivinationResult:
        self.validate(request)
        assert request.event_at is not None

        event_at = request.event_at
        ganzhi: GanzhiInfo = compute_ganzhi(event_at)
        jieqi = current_solar_term(event_at)
        cmonth = lunar_month_chinese(event_at)
        day_gz = ganzhi.day
        hour_gz = ganzhi.hour

        raw: dict[str, Any] = self._Liuren(
            jieqi, cmonth, day_gz, hour_gz
        ).result(0)

        return self._normalize(raw, ganzhi, day_gz, hour_gz)

    def _normalize(
        self, raw: dict[str, Any], ganzhi: GanzhiInfo,
        day_gz: str = "", hour_gz: str = ""
    ) -> DivinationResult:
        """Coerce upstream dict into our standard schema."""
        details: dict[str, Any] = {}

        if "三傳" in raw and isinstance(raw["三傳"], dict):
            san_chuan = raw["三傳"]
            details["san_chuan"] = san_chuan
            initial = san_chuan.get("初傳", [])
            if initial:
                details["initial_branch"] = initial[0]
                details["initial_general"] = initial[1] if len(initial) > 1 else ""
                details["initial_relation"] = initial[2] if len(initial) > 2 else ""

        if "四課" in raw and isinstance(raw["四課"], dict):
            details["si_ke"] = raw["四課"]

        if "天地盤" in raw and isinstance(raw["天地盤"], dict):
            details["tian_di_pan"] = raw["天地盤"]
            # Also expose 地轉天盤 / 地轉天將 for the 式盤 frontend
            sky = raw["天地盤"].get("天盤", [])
            earth = raw["天地盤"].get("地盤", [])
            generals = raw["天地盤"].get("天將", [])
            branch_order = ["巳", "午", "未", "申", "酉", "戌",
                            "亥", "子", "丑", "寅", "卯", "辰"]
            if len(sky) == 12 and len(earth) == 12:
                details["地轉天盤"] = dict(zip(branch_order, sky))
                details["地轉天盤_原"] = dict(zip(branch_order, earth))
            if len(generals) == 12:
                details["地轉天將"] = dict(zip(branch_order, generals))

        if "神煞" in raw and isinstance(raw["神煞"], dict):
            details["shen_sha"] = raw["神煞"]

        details["ge_ju"] = raw.get("格局", [])
        details["ri_ma"] = raw.get("日馬", "")
        details["jieqi"] = raw.get("節氣", "")
        details["lunar_month"] = raw.get("農曆月", "")

        main_judgment_parts: list[str] = []
        if details["ge_ju"]:
            main_judgment_parts.append(f"格局：{'、'.join(details['ge_ju'])}")
        san_chuan = details.get("san_chuan", {})
        if san_chuan.get("初傳"):
            main_judgment_parts.append(
                f"初傳：{san_chuan['初傳'][0]}({san_chuan['初傳'][1] if len(san_chuan['初傳']) > 1 else ''})"
            )
        main_judgment = " | ".join(main_judgment_parts) or "（無判斷）"

        five_elements: list[str] = []
        favorable: list[str] = []
        unfavorable: list[str] = []

        return DivinationResult(
            system_id=self.system_id,
            system_name=self.system_name,
            ganzhi=ganzhi,
            five_elements=five_elements,
            main_judgment=main_judgment,
            favorable=favorable,
            unfavorable=unfavorable,
            details=details,
            raw_output=str(raw),
            computed_at=datetime.utcnow(),
        )
