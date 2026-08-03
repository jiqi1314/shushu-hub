/**
 * 大六壬 — 式盤 SVG rendering.
 * Mirrors kentang's `render_shipan` function in kinliuren/app.py.
 */

const PALACE_POSITIONS = {
  "巳": [12.5, 12.5],
  "午": [37.5, 12.5],
  "未": [62.5, 12.5],
  "申": [87.5, 12.5],
  "酉": [87.5, 37.5],
  "戌": [87.5, 62.5],
  "亥": [87.5, 87.5],
  "子": [62.5, 87.5],
  "丑": [37.5, 87.5],
  "寅": [12.5, 87.5],
  "卯": [12.5, 62.5],
  "辰": [12.5, 37.5],
};

// 28 宿 (反序為活盤)
const MANSION_RING = "角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫";
const MANSION_RING_DISPLAY = MANSION_RING.split("").reverse();
const ZI_TARGET_ANGLE = 161.565051177078;

function escHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/**
 * Render 大六壬式盤.
 * @param {Object} chart - the 日課 chart (with 地轉天盤 / 地轉天將 / 三傳 / 四課)
 * @param {string} activeMansion - 28宿 active mansion (e.g. "房")
 * @param {string} centerContent - HTML for the center (三傳四課)
 * @returns {string} SVG markup
 */
export function renderShipan(chart, activeMansion, centerContent = "") {
  const rotationStep = 360 / MANSION_RING_DISPLAY.length;
  let rotationOffset = 0;
  if (MANSION_RING_DISPLAY.includes(activeMansion)) {
    rotationOffset = ZI_TARGET_ANGLE -
      MANSION_RING_DISPLAY.indexOf(activeMansion) * rotationStep;
  }

  // 12 宮 cells (fixed positions)
  const palaces = [];
  for (const [branch, [left, top]] of Object.entries(PALACE_POSITIONS)) {
    palaces.push(`
      <div class="shipan-cell" style="left:${left}%; top:${top}%;">
        <div class="shipan-cell-general">${escHtml(chart?.["地轉天將"]?.[branch] || "")}</div>
        <div class="shipan-cell-sky">${escHtml(chart?.["地轉天盤"]?.[branch] || "")}</div>
      </div>
    `);
  }

  // 28 宿 ring (rotating with active mansion)
  const fracShift = (rotationOffset * 28) / 360;
  const mansions = [];
  for (let i = 0; i < 28; i++) {
    const posT = ((i + fracShift) % 28 + 28) % 28;
    const side = Math.floor(posT / 7);
    const frac = (posT % 7) / 7;
    let left, top, rot;
    if (side === 0) {        // top
      left = frac * 100; top = 4; rot = 0;
    } else if (side === 1) {  // right
      left = 96; top = frac * 100; rot = 90;
    } else if (side === 2) {  // bottom
      left = (1 - frac) * 100; top = 96; rot = 0;
    } else {                  // left
      left = 4; top = (1 - frac) * 100; rot = -90;
    }
    mansions.push(`
      <div class="shipan-mansion"
           style="left:${left}%; top:${top}%; transform: rotate(${rot}deg);">
        ${escHtml(MANSION_RING_DISPLAY[i])}
      </div>
    `);
  }

  return `
    <div class="shipan-shell">
      <div class="shipan-outer-ring">
        ${mansions.join("")}
      </div>
      <div class="shipan-board">
        ${palaces.join("")}
        <div class="shipan-center-large">
          ${centerContent}
        </div>
      </div>
    </div>
  `;
}

/** Render the three-transmission four-course center text. */
export function renderCenterText(sanChuan, siKe) {
  if (!sanChuan || !siKe) return "";
  const chuan = [
    (sanChuan["初傳"] || []).join(""),
    (sanChuan["中傳"] || []).join(""),
    (sanChuan["末傳"] || []).join(""),
  ];
  // 四課兩行：上課 (each first char of each ke), 下課 (each second char)
  const keOrder = ["四課", "三課", "二課", "一課"];
  const keLine1 = keOrder.map(k => (siKe[k]?.[0]?.[0] || "")).join("");
  const keLine2 = keOrder.map(k => (siKe[k]?.[0]?.[1] || "")).join("");
  return `
    <pre style="font-family: var(--font-mono); color: var(--text-primary);
                 margin:0; padding: 2px 4px; text-align: center;
                 white-space: pre; line-height: 1.15;
                 letter-spacing: 0.05em;">${chuan[0]}
${chuan[1]}
${chuan[2]}

${keLine1}
${keLine2}</pre>
  `;
}

/** Render the 三組並排 (月/日/時). */
export function renderThreeCharts(monthChart, dayChart, hourChart) {
  const renderLine = (chart) => {
    const chuan = chart["三傳"] || {};
    const ke = chart["四課"] || {};
    const siKeOrder = ["四課", "三課", "二課", "一課"];
    const keTop = siKeOrder.map(k => (ke[k]?.[0]?.[0] || "")).join("");
    const keBot = siKeOrder.map(k => (ke[k]?.[0]?.[1] || "")).join("");
    const southBranches = "巳午未申";
    const southGen = southBranches.split("").map(b => chart["地轉天將"]?.[b] || "").join("");
    const southSky = southBranches.split("").map(b => chart["地轉天盤"]?.[b] || "").join("");
    return [
      (chuan["初傳"] || []).join(""),
      (chuan["中傳"] || []).join(""),
      (chuan["末傳"] || []).join(""),
      "",
      keTop,
      keBot,
      southGen,
      southSky,
      southSky,  // middle upper simplified
      southSky,  // middle lower simplified
      southSky,  // north sky simplified
      southGen,  // north general simplified
    ].join("\n");
  };
  return `
    <div class="liuren-three-grid">
      <div class="liuren-three-cell">
        <div class="liuren-three-label">月課</div>
        <pre class="liuren-three-code">${renderLine(monthChart)}</pre>
      </div>
      <div class="liuren-three-cell">
        <div class="liuren-three-label">日課</div>
        <pre class="liuren-three-code">${renderLine(dayChart)}</pre>
      </div>
      <div class="liuren-three-cell">
        <div class="liuren-three-label">時課</div>
        <pre class="liuren-three-code">${renderLine(hourChart)}</pre>
      </div>
    </div>
  `;
}

/** Render 神煞清單. */
export function renderLiurenShenSha(details) {
  const shen = details?.["神煞"];
  if (!shen || typeof shen !== "object") return "";
  const items = Object.entries(shen)
    .filter(([_, v]) => v)
    .map(([k, v]) => `<div class="tag">${k}：${v}</div>`)
    .join("");
  return `<div class="card mt-2"><div class="card-label">神煞</div><div class="shensha-grid mt-1">${items}</div></div>`;
}