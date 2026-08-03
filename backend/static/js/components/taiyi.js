/**
 * 太乙神數 rendering helpers.
 */

const ELEMENT_COLOR = {
  "蛇": "#FF4444", "雀": "#FF4444", "景": "#FF4444", "英": "#FF4444",
  "丁": "#FF4444", "丙": "#FF4444", "巳": "#FF4444", "午": "#FF4444",
  "勾": "#CD853F", "地": "#CD853F", "生": "#CD853F", "死": "#CD853F",
  "任": "#CD853F", "禽": "#CD853F", "芮": "#CD853F", "己": "#CD853F",
  "戊": "#CD853F", "丑": "#CD853F", "辰": "#CD853F", "未": "#CD853F", "戌": "#CD853F",
  "合": "#4CAF50", "符": "#4CAF50", "傷": "#4CAF50", "杜": "#4CAF50",
  "輔": "#4CAF50", "沖": "#4CAF50", "乙": "#4CAF50", "甲": "#4CAF50",
  "寅": "#4CAF50", "卯": "#4CAF50",
  "蓬": "#4499FF", "休": "#4499FF", "玄": "#4499FF", "壬": "#4499FF",
  "癸": "#4499FF", "子": "#4499FF", "亥": "#4499FF",
  "天": "#FFB800", "陰": "#FFB800", "虎": "#FFB800", "開": "#FFB800",
  "驚": "#FFB800", "柱": "#FFB800", "心": "#FFB800", "辛": "#FFB800",
  "庚": "#FFB800", "申": "#FFB800", "酉": "#FFB800",
};

function colorize(text) {
  if (!text) return "";
  return String(text).split("").map(ch => {
    const color = ELEMENT_COLOR[ch];
    return color
      ? `<span style="color:${color};font-weight:600">${ch}</span>`
      : `<span>${ch}</span>`;
  }).join("");
}

/** Render the meta header. */
export function renderTaiyiMeta(details) {
  if (!details) return "";
  const items = [
    ["紀元", details["紀元"]],
    ["太歲", details["太歲"]],
    ["局式", typeof details["局式"] === "object" ? details["局式"]?.["文"] : details["局式"]],
    ["陽九", details["陽九"]],
    ["百六", details["百六"]],
    ["干支", Array.isArray(details["干支"]) ? details["干支"].join(" ") : details["干支"]],
  ].filter(([_, v]) => v);
  const lines = items.map(([k, v]) =>
    `<div class="meta-line"><span class="meta-label">${k}</span><span class="meta-value">${colorize(v)}</span></div>`
  ).join("");
  return lines;
}

/** Render the 9 key cards. */
export function renderTaiyiCards(details) {
  if (!details) return "";
  const cards = [
    ["太乙", details["太乙"], details["太乙落宮"]],
    ["天乙", details["天乙"]],
    ["地乙", details["地乙"]],
    ["四神", details["四神"]],
    ["直符", details["直符"]],
    ["文昌", Array.isArray(details["文昌"]) ? details["文昌"].join("·") : details["文昌"]],
    ["始擊", details["始擊"]],
    ["合神", details["合神"]],
    ["計神", details["計神"]],
  ];
  const html = cards.filter(([_, v]) => v !== undefined && v !== "").map(([label, v, extra]) => `
    <div class="card">
      <div class="card-label">${label}</div>
      <div class="card-value">${colorize(v)}</div>
      ${extra !== undefined ? `<div class="card-subtle">落宮：${extra}</div>` : ""}
    </div>
  `).join("");
  return `<div class="grid-3">${html}</div>`;
}

/** Render the 算 panels (主/客/定). */
export function renderTaiyiSuan(details) {
  if (!details) return "";
  const suan = [
    ["主算", details["主算"]],
    ["客算", details["客算"]],
    ["定算", details["定算"]],
  ];
  return suan.filter(([_, v]) => v).map(([label, val]) => {
    if (!Array.isArray(val) || val.length < 2) return "";
    const [num, meanings] = val;
    const meaning = Array.isArray(meanings) ? meanings.join("；") : "";
    return `
      <div class="card">
        <div class="card-label">${label}</div>
        <div class="card-value" style="font-size:24px;color:var(--gold)">${num}</div>
        <div class="card-subtle">${meaning}</div>
      </div>
    `;
  }).join("");
}

/** Render 神煞清單. */
export function renderShenSha(details) {
  const shen = details?.["神煞"];
  if (!shen || typeof shen !== "object") return "";
  const items = Object.entries(shen)
    .filter(([_, v]) => v)
    .map(([k, v]) => `<div class="tag">${k}：${v}</div>`)
    .join("");
  return `<div class="card"><div class="card-label">神煞</div><div class="mt-2">${items}</div></div>`;
}

/** Full Taiyi dashboard. */
export function renderTaiyiDashboard(result) {
  if (!result || !result.details) return "";
  return `
    ${renderTaiyiMeta(result.details)}
    ${renderTaiyiCards(result.details)}
    <div class="section-title">算</div>
    <div class="grid-3">${renderTaiyiSuan(result.details)}</div>
    ${renderShenSha(result.details)}
  `;
}