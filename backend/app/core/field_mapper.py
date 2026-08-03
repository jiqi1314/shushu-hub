"""Field mapper for cross-system semantic normalization.

Each divination system uses its own vocabulary, but for side-by-side
comparison we want to expose a small, consistent set of semantic buckets
the frontend can render consistently:

  - ganzhi         : 干支四柱 (already canonical, all systems have it)
  - main_judgment  : 主要判斷（一段中文）
  - verdict        : 吉/凶/平 (high-level qualitative)
  - timing         : 時機傾向 — early/mid/late
  - direction      : 方位（如有）
  - key_entities   : 主要用神/神煞/星曜（系統特有的關鍵詞列表）
  - recommendation : 一句話建議（綜合）

The mapper itself does NOT translate traditional interpretations; it only
extracts structured facts. AI synthesis (Phase 4) will do the reading.
"""

from __future__ import annotations

from typing import Any, Literal

from app.schemas.common import DivinationResult

Verdict = Literal["auspicious", "inauspicious", "neutral", "unknown"]
Timing = Literal["early", "mid", "late", "ongoing", "unknown"]


_VERDICT_KEYWORDS_AUSPICIOUS = {
    "吉", "大吉", "亨", "利", "成", "順", "得", "喜", "貴", "福",
    "天乙", "吉神", "旺", "生", "德", "陽",
}

_VERDICT_KEYWORDS_INAUSPICIOUS = {
    "凶", "悔", "吝", "咎", "厲", "喪", "死", "敗", "破", "禍",
    "災", "衰", "墓", "絕", "空", "亡", "伏吟", "反吟",
}

_TIMING_KEYWORDS_EARLY = {
    "初傳", "初爻", "上元", "初限", "寅", "卯",
}
_TIMING_KEYWORDS_MID = {
    "中傳", "中爻", "中元", "中限", "午",
}
_TIMING_KEYWORDS_LATE = {
    "末傳", "上爻", "下元", "末限", "戌", "亥",
}


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(k in text for k in keywords)


def extract_verdict(result: DivinationResult) -> Verdict:
    """Derive a coarse 吉/凶/平 verdict from main_judgment + details."""
    haystack = " ".join(
        [
            result.main_judgment or "",
            str(result.details.get("格局") or ""),
            str(result.details.get("ge_ju") or ""),
        ]
    )
    if not haystack.strip():
        return "unknown"
    has_auspicious = _contains_any(haystack, _VERDICT_KEYWORDS_AUSPICIOUS)
    has_inauspicious = _contains_any(haystack, _VERDICT_KEYWORDS_INAUSPICIOUS)
    if has_auspicious and not has_inauspicious:
        return "auspicious"
    if has_inauspicious and not has_auspicious:
        return "inauspicious"
    if has_auspicious and has_inauspicious:
        return "neutral"
    return "neutral"


def extract_timing(result: DivinationResult) -> Timing:
    """Derive a timing preference (early / mid / late / ongoing) from details."""
    if result.system_id == "liuren":
        san = result.details.get("san_chuan", {})
        if isinstance(san, dict) and san.get("初傳"):
            branch = san["初傳"][0] if san["初傳"] else ""
            if branch in {"寅", "卯"}:
                return "early"
            if branch == "午":
                return "mid"
            if branch in {"戌", "亥"}:
                return "late"
        return "ongoing"
    if result.system_id == "qimen":
        ju_pai = str(result.details.get("排局", ""))
        if "上元" in ju_pai:
            return "early"
        if "中元" in ju_pai:
            return "mid"
        if "下元" in ju_pai:
            return "late"
        return "ongoing"
    if result.system_id == "ichingshifa":
        if result.details.get("zhi_gua_name"):
            return "ongoing"
    if result.system_id == "taiyi":
        scope = result.details.get("scope", "")
        if scope == "nianji":
            return "ongoing"
        if scope in {"shiji", "fenji"}:
            return "early"
        if scope == "yueji":
            return "mid"
    return "unknown"


def extract_key_entities(result: DivinationResult) -> list[str]:
    """Extract the most decision-relevant entities from each system."""
    entities: list[str] = []

    if result.system_id == "liuren":
        san = result.details.get("san_chuan", {})
        if isinstance(san, dict):
            for level in ("初傳", "中傳", "末傳"):
                chuan = san.get(level)
                if isinstance(chuan, list) and chuan:
                    entities.append(f"{level}：{chuan[0]}")
        ge_ju = result.details.get("ge_ju", [])
        if isinstance(ge_ju, list):
            entities.extend(f"格局：{g}" for g in ge_ju if isinstance(g, str))

    elif result.system_id == "qimen":
        for key in ("值符", "值使", "天乙"):
            v = result.details.get(key)
            if v:
                entities.append(f"{key}：{v}")
        zhifu = result.details.get("值符值使", {})
        if isinstance(zhifu, dict):
            for sub in ("值符星宮", "值使門宮"):
                pair = zhifu.get(sub, [])
                if isinstance(pair, list) and len(pair) >= 2:
                    entities.append(f"{sub[2:]}：{pair[0]}({pair[1]})")

    elif result.system_id == "taiyi":
        for key in ("太乙", "天乙", "地乙", "紀元", "太歲"):
            v = result.details.get(key)
            if v is not None and v != "":
                entities.append(f"{key}：{v}")
        ju_shi = result.details.get("局式")
        if isinstance(ju_shi, dict) and ju_shi.get("文"):
            entities.append(f"局式：{ju_shi['文']}")

    elif result.system_id == "ichingshifa":
        for key in ("ben_gua_name", "zhi_gua_name"):
            v = result.details.get(key)
            if v:
                entities.append(f"{'本卦' if key == 'ben_gua_name' else '之卦'}：{v}")
        changed = result.details.get("changed_lines", [])
        if isinstance(changed, list) and changed:
            entities.append(f"動爻：{','.join(str(x) for x in changed)}")

    return entities


def extract_recommendation(result: DivinationResult) -> str:
    """Produce a one-line summary suitable for cross-system comparison."""
    parts: list[str] = []

    parts.append(f"【{result.system_name}】")

    verdict = extract_verdict(result)
    verdict_label = {
        "auspicious": "吉",
        "inauspicious": "凶",
        "neutral": "平",
        "unknown": "—",
    }.get(verdict, "—")
    parts.append(f"傾向：{verdict_label}")

    timing = extract_timing(result)
    timing_label = {
        "early": "早期",
        "mid": "中期",
        "late": "晚期",
        "ongoing": "持續",
        "unknown": "—",
    }.get(timing, "—")
    parts.append(f"時機：{timing_label}")

    if result.main_judgment:
        parts.append(f"判斷：{result.main_judgment}")

    return " | ".join(parts)


def build_cross_analysis(results: list[DivinationResult]) -> dict[str, Any]:
    """Aggregate verdicts and timings across multiple system results."""
    if not results:
        return {"consensus": "unknown", "systems": [], "overlap": [], "differences": []}

    verdicts = [extract_verdict(r) for r in results]
    timings = [extract_timing(r) for r in results]
    entities_by_system: dict[str, list[str]] = {
        r.system_name: extract_key_entities(r) for r in results
    }

    verdict_counts: dict[str, int] = {}
    for v in verdicts:
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    if verdict_counts:
        max_count = max(verdict_counts.values())
        tied = [k for k, v in verdict_counts.items() if v == max_count]
        if len(tied) > 1:
            majority_verdict = "neutral"
        else:
            majority_verdict = tied[0]
    else:
        majority_verdict = "unknown"

    overlapping: list[str] = []
    if len(verdicts) >= 2:
        if verdicts.count(verdicts[0]) == len(verdicts):
            overlapping.append(f"所有系統判斷一致：{verdicts[0]}")
        elif verdicts.count("auspicious") > len(verdicts) / 2:
            overlapping.append("多數系統傾向吉利")
        elif verdicts.count("inauspicious") > len(verdicts) / 2:
            overlapping.append("多數系統傾向不利")
        else:
            overlapping.append("系統間存在分歧")

    if len(timings) >= 2:
        if all(t == "ongoing" for t in timings):
            overlapping.append("時機：所有系統視為持續型")
        elif len(set(timings)) == 1:
            overlapping.append(f"時機：所有系統一致為 {timings[0]}")
        else:
            overlapping.append("時機：不同系統給出不同時間窗")

    differences: list[str] = []
    if len(set(verdicts)) > 1:
        for r, v in zip(results, verdicts, strict=False):
            differences.append(f"{r.system_name}：{v}")

    return {
        "consensus": majority_verdict,
        "verdict_counts": verdict_counts,
        "timings": timings,
        "entities_by_system": entities_by_system,
        "overlap": overlapping,
        "differences": differences,
    }
