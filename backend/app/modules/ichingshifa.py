"""周易筮法 (I-Ching stalk divination) adapter.

Wraps the upstream ``ichingshifa`` library. The upstream library returns
either a formatted board string or a structured dict depending on the
method; we normalize everything into ``DivinationResult``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core import compute_ganzhi
from app.modules.base import BaseModule
from app.schemas.common import DivinationRequest, DivinationResult, GanzhiInfo


class IchingShifaModule(BaseModule):
    """Adapter for kentang2017/ichingshifa."""

    system_id = "ichingshifa"
    system_name = "周易筮法"
    description = "大衍之數起卦，六爻納甲排盤 (Yarrow Stalk Divination)"

    def __init__(self) -> None:
        try:
            from ichingshifa import ichingshifa  # type: ignore
            self._iching = ichingshifa.Iching()
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise RuntimeError(
                "ichingshifa package is required: pip install ichingshifa"
            ) from exc

    def validate(self, request: DivinationRequest) -> None:
        if request.method == "manual":
            if not request.manual_lines:
                raise ValueError("manual_lines is required for method=manual")
            if not all(c in "6789" for c in request.manual_lines):
                raise ValueError("manual_lines must only contain 6/7/8/9")
        if request.method == "datetime":
            if request.event_at is None:
                raise ValueError("datetime is required for method=datetime")

    def compute(self, request: DivinationRequest) -> DivinationResult:
        self.validate(request)
        raw: dict[str, Any] | str = ""
        gz: GanzhiInfo | None = None

        if request.method == "random":
            raw = self._iching.qigua_now()
        elif request.method == "datetime":
            assert request.event_at is not None
            gz = compute_ganzhi(request.event_at)
            raw = self._iching.datetime_bookgua(
                request.event_at.year,
                request.event_at.month,
                request.event_at.day,
                request.event_at.hour,
                request.event_at.minute,
            )
        else:  # manual
            assert request.manual_lines is not None
            if request.event_at is not None:
                gz = compute_ganzhi(request.event_at)
            raw = self._iching.mget_bookgua_details(request.manual_lines)

        return self._normalize(raw, gz)

    def _normalize(
        self, raw: Any, ganzhi: GanzhiInfo | None
    ) -> DivinationResult:
        """Coerce the upstream library's output into our standard schema."""
        details: dict[str, Any] = {}
        main_judgment = ""
        raw_output = ""
        favorable: list[str] = []
        unfavorable: list[str] = []
        five_elements: list[str] = []

        if isinstance(raw, dict):
            raw_output = str(raw)
            ben_gua = raw.get("本卦")
            if isinstance(ben_gua, dict):
                details["ben_gua_name"] = ben_gua.get("卦")
                five_elements = ben_gua.get("五行", []) or []
                favorable = ben_gua.get("六親用神", []) or []
            zhi_gua = raw.get("之卦")
            if isinstance(zhi_gua, dict):
                details["zhi_gua_name"] = zhi_gua.get("卦")
            dayan = raw.get("大衍筮法")
            if isinstance(dayan, list) and dayan:
                main_judgment = "".join(str(x) for x in dayan[2:]) if len(dayan) >= 3 else str(dayan)
            else:
                main_judgment = str(ben_gua.get("卦", "")) if isinstance(ben_gua, dict) else ""
        else:
            raw_output = str(raw)
            main_judgment = raw_output.split("\n", 1)[0][:80]

        return DivinationResult(
            system_id=self.system_id,
            system_name=self.system_name,
            ganzhi=ganzhi,
            five_elements=five_elements,
            main_judgment=main_judgment,
            favorable=favorable,
            unfavorable=unfavorable,
            details=details,
            raw_output=raw_output,
            computed_at=datetime.utcnow(),
        )
