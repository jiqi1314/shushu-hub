"""Tests for the field_mapper module."""

from datetime import datetime

from app.core.field_mapper import (
    build_cross_analysis,
    extract_key_entities,
    extract_recommendation,
    extract_timing,
    extract_verdict,
)
from app.modules.ichingshifa import IchingShifaModule
from app.modules.liuren import LiuRenModule
from app.modules.qimen import QiMenModule
from app.modules.taiyi import TaiYiModule
from app.schemas.common import DivinationRequest, GanzhiInfo


def _make_result(system_id: str, main_judgment: str, details: dict) -> dict:
    """Build a dict-shaped DivinationResult-like object for mapper tests."""
    from app.schemas.common import DivinationResult

    return DivinationResult(
        system_id=system_id,
        system_name=system_id,
        ganzhi=GanzhiInfo(year="甲午", month="癸未", day="丙戌", hour="己未"),
        five_elements=[],
        main_judgment=main_judgment,
        favorable=[],
        unfavorable=[],
        details=details,
        raw_output="",
    )


class TestExtractVerdict:
    def test_auspicious(self) -> None:
        r = _make_result("test", "大吉之象", {})
        assert extract_verdict(r) == "auspicious"

    def test_inauspicious(self) -> None:
        r = _make_result("test", "災禍臨頭", {})
        assert extract_verdict(r) == "inauspicious"

    def test_neutral(self) -> None:
        r = _make_result("test", "吉凶參半", {})
        assert extract_verdict(r) == "neutral"

    def test_unknown_when_empty(self) -> None:
        r = _make_result("test", "", {})
        assert extract_verdict(r) == "unknown"

    def test_via_ge_ju_field(self) -> None:
        r = _make_result("liuren", "", {"ge_ju": ["伏吟", "自任"]})
        assert extract_verdict(r) == "inauspicious"


class TestExtractTiming:
    def test_liuren_san_chuan_branch(self) -> None:
        r = _make_result("liuren", "", {"san_chuan": {"初傳": ["寅"]}})
        assert extract_timing(r) == "early"

    def test_qimen_yuanshang(self) -> None:
        r = _make_result("qimen", "", {"排局": "陰遁七局上元"})
        assert extract_timing(r) == "early"

    def test_qimen_yuanzhong(self) -> None:
        r = _make_result("qimen", "", {"排局": "陽遁五局中元"})
        assert extract_timing(r) == "mid"

    def test_taiyi_scope(self) -> None:
        r = _make_result("taiyi", "", {"scope": "nianji"})
        assert extract_timing(r) == "ongoing"


class TestExtractKeyEntities:
    def test_liuren_extracts_san_chuan(self) -> None:
        r = _make_result(
            "liuren",
            "",
            {
                "san_chuan": {
                    "初傳": ["巳", "空"],
                    "中傳": ["戌"],
                    "末傳": ["卯"],
                },
                "ge_ju": ["伏吟"],
            },
        )
        entities = extract_key_entities(r)
        assert any("初傳" in e for e in entities)
        assert any("伏吟" in e for e in entities)

    def test_qimen_extracts_zhifu(self) -> None:
        r = _make_result(
            "qimen",
            "",
            {
                "值符值使": {
                    "值符星宮": ["心", "坤"],
                    "值使門宮": ["開", "乾"],
                }
            },
        )
        entities = extract_key_entities(r)
        assert any("心" in e and "坤" in e for e in entities)

    def test_taiyi_extracts_ju_shi(self) -> None:
        r = _make_result(
            "taiyi",
            "",
            {"太乙": "坤", "局式": {"文": "陰遁四十局"}},
        )
        entities = extract_key_entities(r)
        assert any("太乙：坤" in e for e in entities)
        assert any("局式" in e for e in entities)

    def test_ichingshifa_extracts_gua(self) -> None:
        r = _make_result(
            "ichingshifa",
            "",
            {"ben_gua_name": "謙", "zhi_gua_name": "升", "changed_lines": [2, 5]},
        )
        entities = extract_key_entities(r)
        assert any("本卦：謙" in e for e in entities)
        assert any("之卦：升" in e for e in entities)
        assert any("動爻" in e for e in entities)


class TestBuildCrossAnalysis:
    def test_empty_input(self) -> None:
        result = build_cross_analysis([])
        assert result["consensus"] == "unknown"

    def test_single_result(self) -> None:
        r = _make_result("ichingshifa", "大吉", {})
        result = build_cross_analysis([r])
        assert result["consensus"] == "auspicious"
        assert "ichingshifa" in result["entities_by_system"]

    def test_multiple_results(self) -> None:
        r1 = _make_result("liuren", "大吉", {"san_chuan": {"初傳": ["寅"]}})
        r2 = _make_result("qimen", "亨通", {"排局": "上元"})
        result = build_cross_analysis([r1, r2])
        assert result["consensus"] == "auspicious"
        assert len(result["overlap"]) > 0

    def test_mixed_verdicts(self) -> None:
        r1 = _make_result("liuren", "大吉", {})
        r2 = _make_result("qimen", "凶象", {})
        result = build_cross_analysis([r1, r2])
        assert result["consensus"] == "neutral"
        assert any("分歧" in o for o in result["overlap"])
        assert len(result["differences"]) == 2


class TestExtractRecommendation:
    def test_includes_system_name_and_verdict(self) -> None:
        r = _make_result("liuren", "格局吉", {})
        rec = extract_recommendation(r)
        assert "【liuren】" in rec
        assert "傾向：吉" in rec


class TestMapperIntegrationWithRealModules:
    """End-to-end: real modules → mapper."""

    def test_liuren_via_mapper(self) -> None:
        module = LiuRenModule()
        req = DivinationRequest(
            system="liuren",
            method="datetime",
            event_at=datetime(2026, 5, 15, 14, 30),
        )
        result = module.compute(req)
        assert extract_verdict(result) in {"auspicious", "inauspicious", "neutral", "unknown"}
        assert extract_key_entities(result)
        rec = extract_recommendation(result)
        assert "【大六壬】" in rec

    def test_all_four_systems_via_cross_analysis(self) -> None:
        req = DivinationRequest(
            system="ichingshifa",
            method="datetime",
            event_at=datetime(2026, 8, 4, 14, 30),
        )
        results = [
            IchingShifaModule().compute(req.model_copy(update={"system": "ichingshifa"})),
            LiuRenModule().compute(req.model_copy(update={"system": "liuren"})),
            QiMenModule().compute(req.model_copy(update={"system": "qimen"})),
            TaiYiModule().compute(req.model_copy(update={"system": "taiyi"})),
        ]
        analysis = build_cross_analysis(results)
        assert analysis["consensus"] in {"auspicious", "inauspicious", "neutral", "unknown"}
        assert len(analysis["entities_by_system"]) == 4
