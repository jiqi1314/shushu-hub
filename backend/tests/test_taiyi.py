"""Tests for the TaiYi (太乙神數) module adapter."""

from datetime import datetime

import pytest

from app.modules import get_module
from app.modules.taiyi import TaiYiModule
from app.schemas.common import DivinationRequest


@pytest.fixture
def taiyi_module() -> TaiYiModule:
    module = get_module("taiyi")
    assert isinstance(module, TaiYiModule)
    return module


class TestTaiYi:
    def test_default_fenji_tongzong(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            timezone="Asia/Hong_Kong",
        )
        result = taiyi_module.compute(request)
        assert result.system_id == "taiyi"
        assert result.system_name == "太乙神數"
        assert result.details["scope"] == "fenji"
        assert result.details["formula"] == "tongzong"
        assert result.details["太乙計"] == "分計"

    def test_nianji_scope(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"scope": "nianji"},
        )
        result = taiyi_module.compute(request)
        assert result.details["scope"] == "nianji"
        assert result.details["太乙計"] == "年計"

    def test_yueji_scope(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"scope": "yueji"},
        )
        result = taiyi_module.compute(request)
        assert result.details["太乙計"] == "月計"

    def test_riji_scope(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"scope": "riji"},
        )
        result = taiyi_module.compute(request)
        assert result.details["太乙計"] == "日計"

    def test_shiji_scope(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"scope": "shiji"},
        )
        result = taiyi_module.compute(request)
        assert result.details["太乙計"] == "時計"

    def test_jinjing_formula(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"formula": "jinjing"},
        )
        result = taiyi_module.compute(request)
        assert result.details["formula"] == "jinjing"
        assert "太乙金鏡" in result.main_judgment

    def test_result_includes_classic_fields(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
        )
        result = taiyi_module.compute(request)
        for key in ("干支", "農曆", "紀元", "太歲", "局式", "太乙", "天乙", "地乙", "主算", "客算"):
            assert key in result.details, f"Missing field: {key}"

    def test_manual_method_rejected(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(
            system="taiyi", method="manual", manual_lines="789789"
        )
        with pytest.raises(ValueError):
            taiyi_module.validate(request)

    def test_missing_datetime_rejected(self, taiyi_module: TaiYiModule) -> None:
        request = DivinationRequest(system="taiyi", method="datetime")
        with pytest.raises(ValueError):
            taiyi_module.validate(request)
