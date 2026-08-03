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

    def _datetime_lines(
        self, year: int, month: int, day: int, hour: int, minute: int
    ) -> str | None:
        """Replicate upstream's datetime_bookgua line-value algorithm.

        Returns the 6-char combine_gua after 變爻 substitution, e.g. "977777"
        for a hexagram with the first line changing. None if upstream's
        internal tables are missing (shouldn't happen in practice).
        """
        try:
            gangzhi = self._iching.gangzhi(year, month, day, hour, minute)
            ld = self._iching.lunar_date_d(year, month, day)
            zhi_code = dict(zip(self._iching.dizhi, range(1, 13)))
            yz_code = zhi_code.get(gangzhi[0][1])
            hz_code = zhi_code.get(gangzhi[3][1])
            cm = ld.get("月")
            cd = ld.get("日")
            eightgua = {
                1: "777", 2: "778", 3: "787", 4: "788",
                5: "877", 6: "878", 7: "887", 8: "888",
            }
            upper_remain = (yz_code + cm + cd + hz_code) % 8
            if upper_remain == 0:
                upper_remain = 8
            lower_remain = (yz_code + cm + cd) % 8
            if lower_remain == 0:
                lower_remain = 8
            combine = list(eightgua[lower_remain] + eightgua[upper_remain])
            bian_yao = (yz_code + cm + cd + hz_code) % 6
            if bian_yao == 0:
                bian_yao = 6
            combine[bian_yao - 1] = (
                combine[bian_yao - 1].replace("7", "9").replace("8", "6")
            )
            return "".join(combine)
        except Exception:
            return None

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
            # bookgua() returns just the 6-char line string
            bookgua_raw = self._iching.bookgua()
            if isinstance(bookgua_raw, str) and len(bookgua_raw) == 6:
                lines = bookgua_raw
        elif request.method == "datetime":
            assert request.event_at is not None
            gz = compute_ganzhi(request.event_at)
            # Compute the line values using upstream's algorithm so the
            # frontend can render the hexagram preview.
            lines = self._datetime_lines(
                request.event_at.year,
                request.event_at.month,
                request.event_at.day,
                request.event_at.hour,
                request.event_at.minute,
            )
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

        # For datetime/random, also compute the line values to feed
        # the frontend hexagram preview. (already computed above)
        if request.manual_lines is not None:
            lines = request.manual_lines

        return self._normalize(raw, gz, lines)

    def _normalize(
        self, raw: Any, ganzhi: GanzhiInfo | None, lines: str | None = None
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
        elif isinstance(raw, tuple) and len(raw) >= 4:
            # datetime_bookgua returns a tuple like
            # ('離之旅', '火火離', '變爻為初九', '履錯然，敬之無咎。')
            raw_output = str(raw)
            ben_zhi = raw[0] or ""
            details["ben_gua_name"] = ben_zhi
            if isinstance(ben_zhi, str) and "之" in ben_zhi:
                parts = ben_zhi.split("之")
                details["ben_gua_name"] = parts[0]
                details["zhi_gua_name"] = parts[1] if len(parts) > 1 else ""
            details["gua_symbol"] = raw[1]
            yao_info = raw[2] or ""
            details["changed_line_text"] = yao_info
            # If we got a separate 6-char line string, store it for the
            # frontend hexagram preview.
            if lines and len(lines) == 6 and all(c in "6789" for c in lines):
                details["lines"] = lines
            main_judgment = " → ".join(str(x) for x in raw if x)
        elif isinstance(raw, str):
            raw_output = raw
            main_judgment = raw.split("\n", 1)[0][:80]
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
