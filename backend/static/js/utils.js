/**
 * Shared utilities: 五色 mapping, formatting, escape, etc.
 */

/** Element color lookup. Used by 奇門九宮 + 太乙. */
export const ELEMENT_COLOR = {
  /* 火 (Fire) — red */
  "蛇": "#FF4444", "雀": "#FF4444", "景": "#FF4444", "英": "#FF4444",
  "丁": "#FF4444", "丙": "#FF4444", "巳": "#FF4444", "午": "#FF4444",
  /* 土 (Earth) — brown */
  "勾": "#CD853F", "地": "#CD853F", "生": "#CD853F", "死": "#CD853F",
  "任": "#CD853F", "禽": "#CD853F", "芮": "#CD853F", "己": "#CD853F",
  "戊": "#CD853F", "丑": "#CD853F", "辰": "#CD853F", "未": "#CD853F", "戌": "#CD853F",
  /* 木 (Wood) — green */
  "合": "#4CAF50", "符": "#4CAF50", "傷": "#4CAF50", "杜": "#4CAF50",
  "輔": "#4CAF50", "沖": "#4CAF50", "乙": "#4CAF50", "甲": "#4CAF50",
  "寅": "#4CAF50", "卯": "#4CAF50",
  /* 水 (Water) — blue */
  "蓬": "#4499FF", "休": "#4499FF", "玄": "#4499FF", "壬": "#4499FF",
  "癸": "#4499FF", "子": "#4499FF", "亥": "#4499FF",
  /* 金 (Metal) — golden */
  "天": "#FFB800", "陰": "#FFB800", "虎": "#FFB800", "開": "#FFB800",
  "驚": "#FFB800", "柱": "#FFB800", "心": "#FFB800", "辛": "#FFB800",
  "庚": "#FFB800", "申": "#FFB800", "酉": "#FFB800",
};

/** Lookup table mapping char → element category. */
export const ELEMENT_OF = {
  "蛇": "fire", "雀": "fire", "景": "fire", "英": "fire",
  "丁": "fire", "丙": "fire", "巳": "fire", "午": "fire",
  "勾": "earth", "地": "earth", "生": "earth", "死": "earth",
  "任": "earth", "禽": "earth", "芮": "earth", "己": "earth",
  "戊": "earth", "丑": "earth", "辰": "earth", "未": "earth", "戌": "earth",
  "合": "wood", "符": "wood", "傷": "wood", "杜": "wood",
  "輔": "wood", "沖": "wood", "乙": "wood", "甲": "wood",
  "寅": "wood", "卯": "wood",
  "蓬": "water", "休": "water", "玄": "water", "壬": "water",
  "癸": "water", "子": "water", "亥": "water",
  "天": "metal", "陰": "metal", "虎": "metal", "開": "metal",
  "驚": "metal", "柱": "metal", "心": "metal", "辛": "metal",
  "庚": "metal", "申": "metal", "酉": "metal",
};

/** Six relatives color. Used by 周易六爻排盤. */
export const RELATIVE_COLOR = {
  "父母": "#9E9E9E",
  "官鬼": "#2D2D2D",
  "妻財": "#C9A14A",
  "兄弟": "#4F7CB8",
  "子孫": "#7AAE5F",
};

/** Six beasts color. */
export const BEAST_COLOR = {
  "青龍": "#4CAF50", "朱雀": "#FF4444", "勾陳": "#CD853F",
  "螣蛇": "#9C27B0", "白虎": "#F5F5F5", "玄武": "#2D2D2D",
};

/** Verdict words that count as auspicious / inauspicious. */
const AUSPICIOUS = ["吉", "大吉", "亨", "利", "成", "順", "得", "喜", "貴", "福",
                    "天乙", "旺", "生", "德", "陽"];
const INAUSPICIOUS = ["凶", "悔", "吝", "咎", "厲", "喪", "死", "敗", "破", "禍",
                      "災", "衰", "墓", "絕", "空", "亡", "伏吟", "反吟"];

export function extractVerdict(text) {
  if (!text) return "unknown";
  const hay = String(text);
  const pos = AUSPICIOUS.some(w => hay.includes(w));
  const neg = INAUSPICIOUS.some(w => hay.includes(w));
  if (pos && !neg) return "auspicious";
  if (neg && !pos) return "inauspicious";
  if (pos && neg) return "neutral";
  return "neutral";
}

export const VERDICT_LABEL = {
  auspicious: "吉",
  inauspicious: "凶",
  neutral: "平",
  unknown: "—",
};

/** HTML escape. */
export function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Format a ganzhi for display (with subtle highlight). */
export function fmtGanzhi(gz) {
  if (!gz) return "";
  const year = `<span style="color:var(--gold)">${esc(gz.year)}</span>`;
  const month = `<span style="color:var(--gold)">${esc(gz.month)}</span>`;
  const day = `<span style="color:var(--gold)">${esc(gz.day)}</span>`;
  const hour = `<span style="color:var(--gold)">${esc(gz.hour)}</span>`;
  return `${year}年 ${month}月 ${day}日 ${hour}時`;
}

/** Branch index (0..11) for the 12 地支. */
export const BRANCH_IDX = {
  "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
  "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11,
};

/** Five-element color for a branch (char → color). */
export function branchColor(b) {
  return ELEMENT_COLOR[b] || "var(--text-primary)";
}

/** Standard 2-char Chinese number for lunar months. */
export const LUNAR_MONTH_CN = [
  "零", "一", "二", "三", "四", "五",
  "六", "七", "八", "九", "十", "十一", "十二",
];

/** Render a value list as compact inline tags. */
export function renderTags(items, opts = {}) {
  if (!items || !items.length) return "";
  const cls = opts.gold ? "tag tag-gold" : "tag";
  return items.map(t => `<span class="${cls}">${esc(t)}</span>`).join(" ");
}

/** Compact display of an object as key/value pairs. */
export function renderKV(obj) {
  return Object.entries(obj || {})
    .filter(([_, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `<div><span class="card-label">${esc(k)}</span> <span class="card-value">${esc(String(v))}</span></div>`)
    .join("");
}

/** Pad number. */
export function pad(n) { return String(n).padStart(2, "0"); }