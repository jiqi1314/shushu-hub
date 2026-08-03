/**
 * 奇門遁甲 — 9 宮 grid rendering.
 * Generates SVG mirroring kentang's kinqimen streamlit app.
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

function elColor(ch) {
  return ELEMENT_COLOR[ch] || "#E8F0FF";
}
function elTspan(ch, defaultColor = "#E8F0FF") {
  const color = ELEMENT_COLOR[ch] || defaultColor;
  return `<tspan fill="${color}">${ch}</tspan>`;
}

/**
 * Render the 9-palace SVG with 五色 coding.
 * Mirrors kentang's `generate_qimen_pan_svg` function.
 */
export function renderQimenGrid(details) {
  if (!details) return "";

  const palaceGrid = [
    ["巽", "離", "坤"],
    ["震", "中", "兌"],
    ["艮", "坎", "乾"],
  ];

  // 馬星 / 空亡 → 對應宮位
  const branchToGong = {
    "子": "坎", "丑": "艮", "寅": "艮", "卯": "震",
    "辰": "巽", "巳": "巽", "午": "離", "未": "坤",
    "申": "坤", "酉": "兌", "戌": "乾", "亥": "乾",
  };

  const maGongs = new Set();
  const horse = details["馬星"] || {};
  if (horse["驛馬"] && branchToGong[horse["驛馬"]]) {
    maGongs.add(branchToGong[horse["驛馬"]]);
  }

  const kongGongs = new Set();
  const kongInfo = details["旬空"] || {};
  const branches = kongInfo["日空"] || "";
  for (let i = 0; i < branches.length; i += 2) {
    const br = branches.substring(i, i + 2);
    if (br && branchToGong[br]) kongGongs.add(branchToGong[br]);
  }

  const svgW = 720, svgH = 720;
  const cell = 200;
  const start = 60;

  const cells = [];
  for (let row = 0; row < palaceGrid.length; row++) {
    for (let col = 0; col < palaceGrid[row].length; col++) {
      const gong = palaceGrid[row][col];
      const x = start + col * cell;
      const y = start + row * cell;

      if (gong === "中") {
        const diZhong = (details["地盤"] || {})["中"] || "";
        cells.push(`
          <rect x="${x}" y="${y}" width="${cell}" height="${cell}" rx="12"
                fill="#152030" stroke="#5A7399" stroke-width="3"/>
          <text x="${x + 16}" y="${y + 34}" fill="#E8F0FF" font-size="24"
                font-weight="bold" font-family="serif">中</text>
          <text x="${x + cell / 2}" y="${y + 120}" text-anchor="middle"
                font-size="56" font-family="serif">${elTspan(diZhong)}</text>
        `);
      } else {
        const shenV = (details["神"] || {})[gong] || "";
        const menV = (details["門"] || {})[gong] || "";
        const tianV = (details["天盤"] || {})[gong] || "";
        const xingV = (details["星"] || {})[gong] || "";
        const diV = (details["地盤"] || {})[gong] || "";

        const annX = x + 40;
        const annY = y + 30;
        const hasMa = maGongs.has(gong);
        const hasKong = kongGongs.has(gong);

        let anns = "";
        if (hasMa) {
          anns += `<text x="${annX}" y="${annY}" fill="#FFD700" font-size="16" font-weight="bold" font-family="serif">馬</text>`;
        }
        if (hasKong) {
          const kx = hasMa ? annX + 18 : annX;
          const ky = annY + (hasMa ? 14 : 0);
          anns += `<text x="${kx}" y="${ky}" fill="#FFD700" font-size="16" font-weight="bold" font-family="serif">空</text>`;
        }

        cells.push(`
          <rect x="${x}" y="${y}" width="${cell}" height="${cell}" rx="12"
                fill="#152030" stroke="#5A7399" stroke-width="3"/>
          <text x="${x + 16}" y="${y + 34}" fill="#E8F0FF" font-size="24"
                font-weight="bold" font-family="serif">${gong}</text>
          ${anns}
          <text x="${x + 62}" y="${y + 88}" text-anchor="middle"
                font-size="30" font-family="serif">${elTspan(xingV)}</text>
          <text x="${x + 138}" y="${y + 88}" text-anchor="middle"
                font-size="30" font-family="serif">${elTspan(tianV)}</text>
          <text x="${x + 62}" y="${y + 132}" text-anchor="middle"
                font-size="30" font-family="serif">${elTspan(shenV)}</text>
          <text x="${x + 62}" y="${y + 174}" text-anchor="middle"
                font-size="30" font-family="serif">${elTspan(menV)}</text>
          <text x="${x + 138}" y="${y + 174}" text-anchor="middle"
                font-size="30" font-family="serif">${elTspan(diV)}</text>
        `);
      }
    }
  }

  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${svgW} ${svgH}"
         style="width:100%;height:auto;display:block;margin:0 auto;">
      <rect width="${svgW}" height="${svgH}" rx="18" fill="#0F1726"/>
      ${cells.join("")}
    </svg>
  `;
}

/** Render the 馬星 / 空亡 / 值符 / 值使 meta. */
export function renderQimenMeta(details) {
  if (!details) return [];
  const items = [
    ["排盤方式", details["排盤方式"]],
    ["排局", details["排局"]],
    ["節氣", details["節氣"]],
    ["值符星宮", details["值符值使"]?.["值符星宮"]?.join(" ")],
    ["值使門宮", details["值符值使"]?.["值使門宮"]?.join(" ")],
  ];
  const lines = items
    .filter(([_, v]) => v)
    .map(([k, v]) =>
      `<div class="meta-line"><span class="meta-label">${k}</span><span class="meta-value">${typeof v === "string" ? v : JSON.stringify(v)}</span></div>`
    );
  return lines.join("");
}

/** Render 馬星 / 空亡 explanation card. */
export function renderQimenShenSha(details) {
  if (!details) return "";
  const horse = details["馬星"] || {};
  const kong = details["旬空"] || {};
  const items = [];
  for (const [k, v] of Object.entries(horse)) {
    if (v) items.push(`<div class="tag">${k}：${v}</div>`);
  }
  if (kong["日空"]) items.push(`<div class="tag tag-gold">日空：${kong["日空"]}</div>`);
  if (kong["時空"]) items.push(`<div class="tag tag-gold">時空：${kong["時空"]}</div>`);
  if (!items.length) return "";
  return `<div class="card mt-2"><div class="card-label">神煞 / 馬星 / 空亡</div><div class="shensha-grid mt-1">${items.join("")}</div></div>`;
}