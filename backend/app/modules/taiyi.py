"""太乙神數 (Tai Yi Shen Shu) adapter.

Wraps the upstream ``kintaiyi`` library. Same broken-package pattern as
``kinqimen``: empty ``__init__.py`` and unqualified ``import config``. We
load the module via ``importlib.util`` to bypass the empty package init.

The upstream ``Taiyi.pan(ji_style, taiyi_acumyear)`` takes two enum-like
parameters:

  - ``ji_style`` (time scope):
      0 = 年計 (year), 1 = 月計 (month), 2 = 日計 (day),
      3 = 時計 (hour),  4 = 分計 (minute)
  - ``taiyi_acumyear`` (公式類別):
      0 = 太乙統宗, 1 = 太乙金鏡, 2 = 太乙淘金歌, 3 = 太乙局

For our purposes the user picks a ``ji_style`` via ``request.details.scope``
(default: ``"fenji"`` / 分計), and ``formula`` via ``request.details.formula``
(default: ``"tongzong"`` / 太乙統宗).
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from app.core import compute_ganzhi
from app.modules.base import BaseModule
from app.schemas.common import DivinationRequest, DivinationResult, GanzhiInfo

TaiYiScope = Literal["nianji", "yueji", "riji", "shiji", "fenji"]
TaiYiFormula = Literal["tongzong", "jinjing", "taojinge", "ju"]


_SCOPE_MAP: dict[TaiYiScope, int] = {
    "nianji": 0,
    "yueji": 1,
    "riji": 2,
    "shiji": 3,
    "fenji": 4,
}

_SCOPE_LABEL: dict[TaiYiScope, str] = {
    "nianji": "年計",
    "yueji": "月計",
    "riji": "日計",
    "shiji": "時計",
    "fenji": "分計",
}

_FORMULA_MAP: dict[TaiYiFormula, int] = {
    "tongzong": 0,
    "jinjing": 1,
    "taojinge": 2,
    "ju": 3,
}

_FORMULA_LABEL: dict[TaiYiFormula, str] = {
    "tongzong": "太乙統宗",
    "jinjing": "太乙金鏡",
    "taojinge": "太乙淘金歌",
    "ju": "太乙局",
}


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively convert numpy scalars to native Python types.

    kintaiyi returns ``numpy.int64`` / ``numpy.str_`` mixed with native
    Python values; Pydantic's serializer rejects the numpy ones.
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        converted = [_sanitize_for_json(v) for v in obj]
        return type(obj)(converted) if isinstance(obj, tuple) else converted
    if isinstance(obj, int | float | str | bool):
        return obj
    if hasattr(obj, "item"):  # numpy scalar
        try:
            return obj.item()
        except (ValueError, TypeError):
            return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return obj


def _load_kintaiyi_module() -> Any:
    """Lazily load the kintaiyi package bypassing its broken ``__init__.py``.

    The upstream ``kintaiyi.py`` does ``from config import ...`` (and many
    other broken-package siblings do similar). To make sure the right
    ``config.py`` resolves, we pre-load kintaiyi's own ``config.py`` into
    ``sys.modules['config']`` before executing the upstream module.
    """
    candidate: Path | None = None
    for p in sys.path:
        guess = Path(p) / "kintaiyi"
        if guess.is_dir() and (guess / "kintaiyi.py").exists():
            candidate = guess
            break

    if candidate is None:
        raise RuntimeError(
            "kintaiyi package directory not found; install with "
            "'pip install --no-deps kintaiyi'"
        )

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    config_path = candidate / "config.py"
    config_spec = importlib.util.spec_from_file_location(
        "_kintaiyi_config", config_path
    )
    if config_spec is None or config_spec.loader is None:
        raise RuntimeError("Could not load kintaiyi config.py")
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    sys.modules["config"] = config_module

    spec = importlib.util.spec_from_file_location(
        "_kintaiyi_impl", candidate / "kintaiyi.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load kintaiyi.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TaiYiModule(BaseModule):
    """Adapter for kentang2017/kintaiyi."""

    system_id = "taiyi"
    system_name = "太乙神數"
    description = "三式之末，年計/月計/日計/時計/分計 (Tai Yi Shen Shu)"

    def __init__(self) -> None:
        self._Taiyi = _load_kintaiyi_module().Taiyi

    def validate(self, request: DivinationRequest) -> None:
        if request.method == "manual":
            raise ValueError("太乙神數 does not support manual method; use datetime")
        if request.event_at is None:
            raise ValueError("event_at (datetime) is required for 太乙神數")

    def compute(self, request: DivinationRequest) -> DivinationResult:
        self.validate(request)
        assert request.event_at is not None

        event_at = request.event_at
        ganzhi: GanzhiInfo = compute_ganzhi(event_at)

        scope = self._resolve_scope(request)
        formula = self._resolve_formula(request)

        taiyi = self._Taiyi(
            event_at.year,
            event_at.month,
            event_at.day,
            event_at.hour,
            event_at.minute,
        )
        raw: dict[str, Any] = taiyi.pan(_SCOPE_MAP[scope], _FORMULA_MAP[formula])

        return self._normalize(raw, ganzhi, scope, formula)

    @staticmethod
    def _resolve_scope(request: DivinationRequest) -> TaiYiScope:
        if request.details and "scope" in request.details:
            v = request.details["scope"]
            if v in _SCOPE_MAP:
                return v  # type: ignore[return-value]
        return "fenji"

    @staticmethod
    def _resolve_formula(request: DivinationRequest) -> TaiYiFormula:
        if request.details and "formula" in request.details:
            v = request.details["formula"]
            if v in _FORMULA_MAP:
                return v  # type: ignore[return-value]
        return "tongzong"

    def _normalize(
        self,
        raw: dict[str, Any],
        ganzhi: GanzhiInfo,
        scope: TaiYiScope,
        formula: TaiYiFormula,
    ) -> DivinationResult:
        sanitized = _sanitize_for_json(raw)
        details: dict[str, Any] = sanitized
        details["scope"] = scope
        details["formula"] = formula

        method_label = f"{_SCOPE_LABEL[scope]} · {_FORMULA_LABEL[formula]}"
        ju_shi = raw.get("局式", {}) or {}
        if isinstance(ju_shi, dict) and ju_shi.get("文"):
            method_label += f" | {ju_shi['文']}"
        taiyi_pos = raw.get("太乙落宮") or raw.get("太乙") or ""
        ji_nian = raw.get("紀元", "")
        tai_sui = raw.get("太歲", "")

        main_parts = [method_label]
        if ji_nian:
            main_parts.append(f"紀元：{ji_nian}")
        if tai_sui:
            main_parts.append(f"太歲：{tai_sui}")
        if taiyi_pos:
            main_parts.append(f"太乙：{taiyi_pos}")
        main_judgment = " | ".join(p for p in main_parts if p)

        return DivinationResult(
            system_id=self.system_id,
            system_name=self.system_name,
            ganzhi=ganzhi,
            five_elements=[],
            main_judgment=main_judgment,
            favorable=[],
            unfavorable=[],
            details=details,
            raw_output=str(sanitized),
            computed_at=datetime.utcnow(),
        )
