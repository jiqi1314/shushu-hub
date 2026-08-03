"""Tests for the QiMen (奇門遁甲) module adapter."""

from datetime import datetime

import pytest

from app.modules import get_module
from app.modules.qimen import QiMenModule
from app.schemas.common import DivinationRequest


@pytest.fixture
def qimen_module() -> QiMenModule:
    module = get_module("qimen")
    assert isinstance(module, QiMenModule)
    return module


class TestQiMen:
    def test_default_variant_chabu(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(
            system="qimen",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            timezone="Asia/Hong_Kong",
        )
        result = qimen_module.compute(request)
        assert result.system_id == "qimen"
        assert result.system_name == "奇門遁甲"
        assert result.details["variant"] == "chabu"
        assert "排盤方式" in result.details
        assert result.details["排盤方式"] == "拆補"

    def test_zhirun_variant(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(
            system="qimen",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"variant": "zhirun"},
        )
        result = qimen_module.compute(request)
        assert result.details["variant"] == "zhirun"
        assert result.details["排盤方式"] == "置閏"

    def test_ke_chabu_variant(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(
            system="qimen",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"variant": "ke_chabu"},
        )
        result = qimen_module.compute(request)
        assert result.details["variant"] == "ke_chabu"

    def test_jinhanyujing_variant(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(
            system="qimen",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            details={"variant": "jinhanyujing"},
        )
        result = qimen_module.compute(request)
        assert result.details["variant"] == "jinhanyujing"

    def test_result_includes_classic_fields(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(
            system="qimen",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
        )
        result = qimen_module.compute(request)
        for key in ("天盤", "地盤", "門", "星", "神", "值符值使"):
            assert key in result.details, f"Missing field: {key}"

    def test_manual_method_rejected(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(
            system="qimen", method="manual", manual_lines="789789"
        )
        with pytest.raises(ValueError):
            qimen_module.validate(request)

    def test_missing_datetime_rejected(self, qimen_module: QiMenModule) -> None:
        request = DivinationRequest(system="qimen", method="datetime")
        with pytest.raises(ValueError):
            qimen_module.validate(request)
