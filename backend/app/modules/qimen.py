"""奇門遁甲 (Qi Men Dun Jia) adapter.

Wraps the upstream ``kinqimen`` library. The upstream package ships an
empty ``__init__.py`` and uses an unqualified ``import config`` in its main
module, which only works if its package directory is on ``sys.path``. We
work around this by lazily loading the module via ``importlib.util`` on
first use.

Supports four chart variants:
  - ``method=datetime`` + ``variant=chabu`` (default): 時家拆補法
  - ``method=datetime`` + ``variant=zhirun``:   時家置閏法
  - ``method=datetime`` + ``variant=ke_chabu``: 刻家拆補法 (minute-level)
  - ``method=datetime`` + ``variant=jinhanyujing``: 金函玉鏡日家奇門
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

QiMenVariant = Literal["chabu", "zhirun", "ke_chabu", "ke_zhirun", "jinhanyujing"]


def _load_kinqimen_module() -> Any:
    """Lazily load the kinqimen package bypassing its broken ``__init__.py``.

    The upstream ``kinqimen.py`` does ``import config`` (unqualified). When
    multiple broken packages (``kinqimen`` and ``kintaiyi``) live next to
    each other on ``sys.path``, both have a ``config.py`` and the wrong
    one gets picked up depending on path ordering. We work around this by
    pre-loading kinqimen's own ``config.py`` into ``sys.modules['config']``
    before executing the upstream module.
    """
    candidate: Path | None = None
    for p in sys.path:
        guess = Path(p) / "kinqimen"
        if guess.is_dir() and (guess / "kinqimen.py").exists():
            candidate = guess
            break

    if candidate is None:
        raise RuntimeError(
            "kinqimen package directory not found; install with "
            "'pip install --no-deps kinqimen'"
        )

    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

    config_path = candidate / "config.py"
    config_spec = importlib.util.spec_from_file_location(
        "_kinqimen_config", config_path
    )
    if config_spec is None or config_spec.loader is None:
        raise RuntimeError("Could not load kinqimen config.py")
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    sys.modules["config"] = config_module

    spec = importlib.util.spec_from_file_location(
        "_kinqimen_impl", candidate / "kinqimen.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load kinqimen.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QiMenModule(BaseModule):
    """Adapter for kentang2017/kinqimen."""

    system_id = "qimen"
    system_name = "奇門遁甲"
    description = "時家奇門、刻家奇門、金函玉鏡日家奇門 (Qi Men Dun Jia)"

    def __init__(self) -> None:
        self._Qimen = _load_kinqimen_module().Qimen

    def validate(self, request: DivinationRequest) -> None:
        if request.method == "manual":
            raise ValueError("奇門遁甲 does not support manual method; use datetime")
        if request.event_at is None:
            raise ValueError("event_at (datetime) is required for 奇門遁甲")

    def compute(self, request: DivinationRequest) -> DivinationResult:
        self.validate(request)
        assert request.event_at is not None

        event_at = request.event_at
        ganzhi: GanzhiInfo = compute_ganzhi(event_at)

        qimen = self._Qimen(
            event_at.year,
            event_at.month,
            event_at.day,
            event_at.hour,
            event_at.minute,
        )

        variant: QiMenVariant = self._resolve_variant(request)
        raw: dict[str, Any] = self._dispatch(qimen, variant)

        return self._normalize(raw, ganzhi, variant)

    @staticmethod
    def _resolve_variant(request: DivinationRequest) -> QiMenVariant:
        """Pick a chart variant from request details, defaulting to chabu."""
        if request.details and "variant" in request.details:
            v = request.details["variant"]
            if v in ("chabu", "zhirun", "ke_chabu", "ke_zhirun", "jinhanyujing"):
                return v  # type: ignore[return-value]
        return "chabu"

    @staticmethod
    def _dispatch(qimen: Any, variant: QiMenVariant) -> dict[str, Any]:
        if variant == "chabu":
            return qimen.pan(1)
        if variant == "zhirun":
            return qimen.pan(2)
        if variant == "ke_chabu":
            return qimen.pan_minute(1)
        if variant == "ke_zhirun":
            return qimen.pan_minute(2)
        if variant == "jinhanyujing":
            return qimen.gpan()
        raise ValueError(f"Unknown variant: {variant}")

    def _normalize(
        self,
        raw: dict[str, Any],
        ganzhi: GanzhiInfo,
        variant: QiMenVariant,
    ) -> DivinationResult:
        details: dict[str, Any] = dict(raw)
        details["variant"] = variant

        method_label = {
            "chabu": "時家拆補",
            "zhirun": "時家置閏",
            "ke_chabu": "刻家拆補",
            "ke_zhirun": "刻家置閏",
            "jinhanyujing": "金函玉鏡日家",
        }[variant]

        ju_pai = raw.get("排局", "")
        jieqi = raw.get("節氣", "")
        zhifu = raw.get("值符值使", {})

        main_parts: list[str] = [method_label]
        if ju_pai:
            main_parts.append(ju_pai)
        if jieqi:
            main_parts.append(f"節氣：{jieqi}")
        if isinstance(zhifu, dict):
            vfg = zhifu.get("值符星宮", [])
            vfm = zhifu.get("值使門宮", [])
            if len(vfg) >= 2:
                main_parts.append(f"值符：{vfg[0]}({vfg[1]})")
            if len(vfm) >= 2:
                main_parts.append(f"值使：{vfm[0]}({vfm[1]})")
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
            raw_output=str(raw),
            computed_at=datetime.utcnow(),
        )
