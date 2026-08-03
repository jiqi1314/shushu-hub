"""Tests for the LiuRen (大六壬) module adapter."""

from datetime import datetime

import pytest

from app.modules import get_module
from app.modules.liuren import LiuRenModule
from app.schemas.common import DivinationRequest


@pytest.fixture
def liuren_module() -> LiuRenModule:
    module = get_module("liuren")
    assert isinstance(module, LiuRenModule)
    return module


class TestLiuRen:
    def test_datetime_method_produces_result(self, liuren_module: LiuRenModule) -> None:
        request = DivinationRequest(
            system="liuren",
            method="datetime",
            event_at=datetime(2026, 5, 15, 14, 30),
            timezone="Asia/Hong_Kong",
        )
        result = liuren_module.compute(request)
        assert result.system_id == "liuren"
        assert result.system_name == "大六壬"
        assert result.ganzhi is not None
        assert len(result.ganzhi.day) == 2

    def test_result_includes_san_chuan(self, liuren_module: LiuRenModule) -> None:
        request = DivinationRequest(
            system="liuren",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
        )
        result = liuren_module.compute(request)
        assert "san_chuan" in result.details
        san_chuan = result.details["san_chuan"]
        assert "初傳" in san_chuan
        assert "中傳" in san_chuan
        assert "末傳" in san_chuan

    def test_result_includes_ge_ju(self, liuren_module: LiuRenModule) -> None:
        request = DivinationRequest(
            system="liuren",
            method="datetime",
            event_at=datetime(2026, 5, 15, 14, 30),
        )
        result = liuren_module.compute(request)
        assert "ge_ju" in result.details
        assert isinstance(result.details["ge_ju"], list)

    def test_manual_method_rejected(self, liuren_module: LiuRenModule) -> None:
        request = DivinationRequest(
            system="liuren",
            method="manual",
            manual_lines="789789",
        )
        with pytest.raises(ValueError):
            liuren_module.validate(request)

    def test_missing_datetime_rejected(self, liuren_module: LiuRenModule) -> None:
        request = DivinationRequest(system="liuren", method="datetime")
        with pytest.raises(ValueError):
            liuren_module.validate(request)

    def test_random_method_rejected(self, liuren_module: LiuRenModule) -> None:
        request = DivinationRequest(system="liuren", method="random")
        with pytest.raises(ValueError):
            liuren_module.validate(request)
