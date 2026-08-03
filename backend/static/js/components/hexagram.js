/**
 * 六爻 (周易) rendering helpers.
 * Used by Tab 1 (周易 detail) and Tab 0 (cross-system overview).
 */

const YAO_LABEL = { "6": "老陰", "7": "少陽", "8": "少陰", "9": "老陽" };

const YAO_POSITIONS = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];

/** Render a single 爻 line with mark for changed lines. */
function yaoLine(val) {
  if (!val) {
    return '<div class="yl-ghost"></div>';
  }
  const isYin = val === "6" || val === "8";
  const mark = val === "6" ? "×" : val === "9" ? "○" : "";
  const inner = isYin
    ? '<span class="seg"></span><span class="gap"></span><span class="seg"></span>'
    : '<span class="seg full"></span>';
  return `
    <div class="yao-line ${isYin ? "yin" : "yang"}">
      ${inner}
      ${mark ? `<span class="mark">${mark}</span>` : ""}
    </div>
  `;
}

/** Render the full hexagram preview (6 lines, bottom to top). */
export function renderHexagramPreview(lines, title = "卦象預覽") {
  const padded = (lines || []).concat(new Array(6 - (lines || []).length).fill(""));
  const rows = padded
    .slice()
    .reverse()
    .map((v, i) => {
      const pos = YAO_POSITIONS[5 - i];
      return `
        <div class="hex-row">
          <span class="hex-pos">${pos}</span>
          ${yaoLine(v)}
          <span class="hex-label">${YAO_LABEL[v] || ""}</span>
        </div>
      `;
    })
    .join("");

  const dots = Array.from({ length: 6 }, (_, i) => {
    let cls = "hex-dot";
    if ((lines || []).length > i) cls += " done";
    else if ((lines || []).length === i && lines?.length) cls += " cur";
    return `<span class="${cls}"></span>`;
  }).join("");

  // If we have a 6-line result, derive names (ben/zhi)
  let nameLine = "";
  if (lines && lines.length === 6) {
    const zhiGua = lines.map(v => v === "6" ? "7" : v === "9" ? "8" : v).join("");
    nameLine = `<div class="hex-names">${lines.join("")} → 之 ${zhiGua}</div>`;
  }

  return `
    <div class="hex-preview">
      <div class="hex-title">${title}</div>
      <div class="hex-rows">${rows}</div>
      <div class="hex-dots">${dots}</div>
      ${nameLine}
    </div>
  `;
}

/** Render the 6-row 排盤 text (六親/六獸/世應/伏神/納甲/五行). */
export function renderPanText(panString) {
  // Wrap in a code-block, preserving monospace formatting
  return `<div class="code-block">${escHtml(panString)}</div>`;
}

function escHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}