"""Tests for the ichingshifa module adapter."""

from datetime import datetime

import pytest

from app.modules import get_module
from app.modules.ichingshifa import IchingShifaModule
from app.schemas.common import DivinationRequest


@pytest.fixture
def iching_module() -> IchingShifaModule:
    module = get_module("ichingshifa")
    assert isinstance(module, IchingShifaModule)
    return module


class TestIchingShifaRandom:
    def test_random_method_produces_result(self, iching_module: IchingShifaModule) -> None:
        request = DivinationRequest(system="ichingshifa", method="random")
        result = iching_module.compute(request)
        assert result.system_id == "ichingshifa"
        assert result.raw_output


class TestIchingShifaDatetime:
    def test_datetime_method_produces_result(self, iching_module: IchingShifaModule) -> None:
        request = DivinationRequest(
            system="ichingshifa",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
            timezone="Asia/Hong_Kong",
        )
        result = iching_module.compute(request)
        assert result.system_id == "ichingshifa"
        assert result.ganzhi is not None
        assert len(result.ganzhi.year) == 2


class TestIchingShifaManual:
    def test_manual_method_produces_result(self, iching_module: IchingShifaModule) -> None:
        request = DivinationRequest(
            system="ichingshifa",
            method="manual",
            manual_lines="789789",
            event_at=datetime(2026, 8, 4, 14, 30),
        )
        result = iching_module.compute(request)
        assert result.system_id == "ichingshifa"
        assert result.raw_output

    def test_manual_rejects_invalid_chars(self, iching_module: IchingShifaModule) -> None:
        request = DivinationRequest(
            system="ichingshifa",
            method="manual",
            manual_lines="123456",
        )
        with pytest.raises(ValueError):
            iching_module.validate(request)
