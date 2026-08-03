/**
 * shushu-hub main app shell + tab router.
 * - Renders top bar with shared input (date/time/timezone/question)
 * - Switches tabs based on URL hash
 * - Loads each tab's content via dynamic import
 */

import { api, ai } from "./api.js";
import { store, datetimeISO, subscribe } from "./state.js";
import {
  esc, fmtGanzhi, extractVerdict, VERDICT_LABEL,
  renderTags, pad
} from "./utils.js";
import {
  renderHexagramPreview, renderPanText
} from "./components/hexagram.js";
import {
  renderTaiyiDashboard
} from "./components/taiyi.js";
import {
  renderQimenGrid, renderQimenMeta, renderQimenShenSha
} from "./components/qimen.js";
import {
  renderShipan, renderCenterText, renderThreeCharts, renderLiurenShenSha
} from "./components/liuren.js";

const TABS = ["overview", "ichingshifa", "liuren", "qimen", "taiyi"];

// ===================== Top bar wiring =====================

function bindTopbar() {
  const s = store.get();
  document.getElementById("topbar-date").value = s.date;
  document.getElementById("topbar-time").value = s.time;
  document.getElementById("topbar-timezone").value = s.timezone;
  document.getElementById("topbar-question").value = s.question;
  document.getElementById("topbar-true-solar").checked = s.use_true_solar_time;

  const onChange = () => {
    store.set({
      date: document.getElementById("topbar-date").value,
      time: document.getElementById("topbar-time").value,
      timezone: document.getElementById("topbar-timezone").value,
      question: document.getElementById("topbar-question").value,
      use_true_solar_time: document.getElementById("topbar-true-solar").checked,
    });
  };
  ["topbar-date", "topbar-time", "topbar-timezone", "topbar-question"].forEach(id =>
    document.getElementById(id).addEventListener("change", onChange));
  document.getElementById("topbar-true-solar")
    .addEventListener("change", onChange);

  document.getElementById("topbar-submit").addEventListener("click", () => {
    const tab = currentTab();
    // Each tab listens to a custom event "shushu:rerun" to re-run
    window.dispatchEvent(new CustomEvent("shushu:rerun", { detail: { tab } }));
  });
}

// ===================== Tab router =====================

function currentTab() {
  const hash = window.location.hash.replace(/^#/, "");
  return TABS.includes(hash) ? hash : "overview";
}

function switchTab(tab) {
  if (!TABS.includes(tab)) tab = "overview";
  history.replaceState(null, "", `#${tab}`);
  document.querySelectorAll("#tab-nav button").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === tab);
  });
  document.querySelectorAll(".tab-content").forEach(s => {
    s.classList.toggle("active", s.id === `tab-${tab}`);
  });
  renderTab(tab);
}

document.getElementById("tab-nav").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-tab]");
  if (btn) switchTab(btn.dataset.tab);
});

window.addEventListener("hashchange", () => switchTab(currentTab()));

// ===================== Per-tab renderers =====================

async function renderTab(tab) {
  const root = document.getElementById(`tab-${tab}`);
  if (!root) return;
  if (tab === "overview") return renderOverview(root);
  if (tab === "ichingshifa") return renderIchingshifa(root);
  if (tab === "liuren") return renderLiuren(root);
  if (tab === "qimen") return renderQimen(root);
  if (tab === "taiyi") return renderTaiyi(root);
}

// ---------- Overview (cross-system) ----------

async function renderOverview(root) {
  const s = store.get();
  root.innerHTML = `
    <h2 style="margin-bottom:14px;">🔮 跨系統並排</h2>
    <p class="text-secondary text-small">
      點擊右上「🔮 起卦」即可同時呼叫 ${s.use_true_solar_time ? "（含真太陽時）" : ""}多個系統並排比較。
      你也可以從側邊欄切換到單一系統的詳細頁。
    </p>
    <div id="overview-status" class="text-dim text-small"></div>
    <div id="overview-results"></div>
  `;
  runOverview();
}

async function runOverview() {
  const s = store.get();
  const status = document.getElementById("overview-status");
  const results = document.getElementById("overview-results");
  status.innerHTML = `<div class="loading-block"><div class="loading"></div><div>排盤中...</div></div>`;
  try {
    const data = await api.compare({
      datetime: datetimeISO(),
      timezone: s.timezone,
      question: s.question,
      use_true_solar_time: s.use_true_solar_time,
    });
    renderOverviewResults(data, results);
    status.innerHTML = "";
  } catch (e) {
    status.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

function renderOverviewResults(data, container) {
  const { results, cross_analysis, failures } = data;
  const ca = cross_analysis || {};

  const verdictBadges = ["auspicious", "inauspicious", "neutral", "unknown"]
    .filter(v => (ca.verdict_counts || {})[v])
    .map(v => `<span class="verdict ${v}">${VERDICT_LABEL[v]} × ${ca.verdict_counts[v]}</span>`)
    .join(" ");

  let html = `
    <div class="card card-vermilion mt-3">
      <h3>🔍 跨系統分析</h3>
      <div class="mt-2 text-small">
        共識：<span class="text-gold" style="font-weight:600;">${esc(ca.consensus || "—")}</span>
        ${verdictBadges ? ` · ${verdictBadges}` : ""}
      </div>
      ${(ca.overlap || []).length ? `
        <div class="mt-2"><strong class="text-secondary text-small">共同點</strong>
          <ul style="margin:6px 0 0 20px;">
            ${ca.overlap.map(o => `<li class="text-small">${esc(o)}</li>`).join("")}
          </ul>
        </div>` : ""}
      ${(ca.differences || []).length ? `
        <div class="mt-2"><strong class="text-secondary text-small">分歧</strong>
          <ul style="margin:6px 0 0 20px;">
            ${ca.differences.map(d => `<li class="text-small">${esc(d)}</li>`).join("")}
          </ul>
        </div>` : ""}
    </div>
  `;

  html += '<div class="grid-2 mt-3">';
  for (const r of results) {
    const ents = (ca.entities_by_system || {})[r.system_name] || [];
    html += `
      <div class="card card-gold">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <h3>${esc(r.system_name)}</h3>
          <span class="text-tiny text-secondary">${esc(r.system_id)}</span>
        </div>
        <div class="mt-1 text-small text-secondary">${fmtGanzhi(r.ganzhi)}</div>
        <div class="subtle-block mt-1">${esc(r.main_judgment || "（無判斷）")}</div>
        ${ents.length ? `<div class="mt-2">${renderTags(ents.slice(0, 6))}</div>` : ""}
      </div>
    `;
  }
  html += "</div>";

  if (failures.length) {
    html += `<div class="error-block mt-2"><strong>部分失敗：</strong><ul style="margin-top:6px;padding-left:20px;">${
      failures.map(f => `<li>${esc(f.system)}: ${esc(f.message)}</li>`).join("")
    }</ul></div>`;
  }

  container.innerHTML = html;
}

// ---------- Ichingshifa ----------

async function renderIchingshifa(root) {
  root.innerHTML = `
    <h2 style="margin-bottom:14px;">☯️ 周易 · 堅六爻</h2>
    <p class="quote">
      「大衍之數五十，其用四十有九。分而為二以像兩，掛一以像三，
      揲之以四以像四時，歸奇於扐以像閏。五歲再閏，故再扐而後掛。」
      ——《周易·繫辭傳》
    </p>

    <div class="status-row">
      <span class="mode-badge auto" id="iching-mode-badge">🤖 時間盤</span>
      <span class="text-secondary text-small" id="iching-mode-desc">依輸入時間起卦</span>
    </div>

    <div class="iching-grid">
      <div class="iching-main">
        <div class="hex-preview" id="iching-hex">
          ${renderHexagramPreview([], "等待起卦")}
        </div>
        <div class="code-block" id="iching-pan" style="min-height:60px;">（尚未起卦）</div>
        <div class="action-bar">
          <button class="btn btn-primary" id="iching-run-btn">🔮 立即起卦</button>
          <button class="btn" id="iching-ai-btn">🔍 AI 分析</button>
        </div>
        <div id="iching-ai-result"></div>
      </div>
      <aside>
        <div class="card">
          <h4 class="card-label">起卦方式</h4>
          <div class="status-row mt-2">
            <label class="chip active" data-mode="auto"><input type="radio" name="iching-mode" value="auto" checked /> 時間</label>
            <label class="chip" data-mode="random"><input type="radio" name="iching-mode" value="random" /> 隨機</label>
          </div>
          <hr/>
          <div id="iching-manual-block" style="display:none;">
            <h4 class="card-label">手動輸入爻值（由初爻至上爻）</h4>
            <div class="grid-2 mt-1" style="gap:8px;">
              ${["上", "五", "四", "三", "二", "初"].map(p => `
                <div>
                  <label class="card-label">${p}爻</label>
                  <select class="manual-yao" data-pos="${p}" style="width:100%;background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border-subtle);border-radius:6px;padding:6px;">
                    <option value="7">少陽 ⚊</option>
                    <option value="8">少陰 ⚋</option>
                    <option value="9">老陽 ⚊○</option>
                    <option value="6">老陰 ⚋×</option>
                  </select>
                </div>
              `).join("")}
            </div>
          </div>
        </div>
      </aside>
    </div>
  `;
  bindIchingshifaHandlers();
}

let ichingState = { lines: [], mode: "auto", manual: "777777", panText: "", panMeta: {} };

function bindIchingshifaHandlers() {
  // Mode toggle
  document.querySelectorAll('label[data-mode]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('label[data-mode]').forEach(x => x.classList.remove('active'));
      el.classList.add('active');
      const mode = el.dataset.mode;
      ichingState.mode = mode;
      document.getElementById('iching-manual-block').style.display = mode === 'auto' ? 'none' : 'block';
      const badge = document.getElementById('iching-mode-badge');
      const desc = document.getElementById('iching-mode-desc');
      if (mode === 'auto') {
        badge.className = 'mode-badge auto';
        badge.textContent = '🤖 時間盤';
        desc.textContent = '依輸入時間起卦';
      } else {
        badge.className = 'mode-badge random';
        badge.textContent = '🎲 隨機盤';
        desc.textContent = '使用大衍筮法隨機起卦';
      }
    });
  });

  // Manual yao selectors
  document.querySelectorAll('.manual-yao').forEach(sel => {
    sel.addEventListener('change', () => {
      const vals = ["初", "二", "三", "四", "五", "上"]
        .map(p => document.querySelector(`.manual-yao[data-pos="${p}"]`).value);
      ichingState.manual = vals.join("");
    });
  });
  // Initialize manual state
  const vals0 = ["初", "二", "三", "四", "五", "上"]
    .map(p => document.querySelector(`.manual-yao[data-pos="${p}"]`).value);
  ichingState.manual = vals0.join("");

  document.getElementById('iching-run-btn').addEventListener('click', runIchingshifa);
  document.getElementById('iching-ai-btn').addEventListener('click', aiAnalyzeIching);
  window.addEventListener('shushu:rerun', (e) => {
    if (e.detail.tab === 'ichingshifa') runIchingshifa();
  });

  // Auto-run on first load
  runIchingshifa();
}

async function runIchingshifa() {
  const s = store.get();
  const hexEl = document.getElementById('iching-hex');
  const panEl = document.getElementById('iching-pan');
  hexEl.innerHTML = renderHexagramPreview([], "排盤中...");
  panEl.textContent = "（排盤中...）";
  try {
    const req = {
      system: 'ichingshifa',
      method: ichingState.mode === 'auto' ? 'datetime' : 'random',
      datetime: datetimeISO(),
      timezone: s.timezone,
      manual_lines: ichingState.mode === 'random' ? ichingState.manual : undefined,
    };
    const result = await api.divination(req);
    ichingState.lines = parseLinesFromResult(result);
    ichingState.panText = result.raw_output || formatPanFromDict(result.details);
    ichingState.panMeta = result;
    hexEl.innerHTML = renderHexagramPreview(ichingState.lines, `${result.details?.ben_gua_name || ''}${result.details?.zhi_gua_name ? ' → '+result.details.zhi_gua_name : ''}`);
    panEl.innerHTML = `<pre style="margin:0;font-family:var(--font-mono);white-space:pre;">${esc(ichingState.panText)}</pre>`;
  } catch (e) {
    hexEl.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
    panEl.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

function parseLinesFromResult(result) {
  const d = result.details || {};
  const raw = result.raw_output || "";
  const m = String(raw).match(/[6789]{6}/);
  if (m) return m[0].split("");
  return [];
}

function formatPanFromDict(details) {
  if (!details) return "";
  const lines = [];
  if (details.ben_gua_name) lines.push(`本卦：${details.ben_gua_name}`);
  if (details.zhi_gua_name) lines.push(`之卦：${details.zhi_gua_name}`);
  if (details.changed_lines) lines.push(`動爻：${(details.changed_lines || []).join(",")}`);
  return lines.join("\n");
}

async function aiAnalyzeIching() {
  const s = store.get();
  if (!ichingState.panText) return;
  const out = document.getElementById('iching-ai-result');
  out.innerHTML = `<div class="ai-section"><div class="loading-block"><div class="loading"></div><div>AI 分析中...</div></div></div>`;
  try {
    const text = await callAI([
      { role: 'system', content: '你是一位精通周易六爻的大師。請根據提供的六爻排盤結果進行簡明分析（300字內）。' },
      { role: 'user', content: `六爻排盤：\n${ichingState.panText}` },
    ]);
    out.innerHTML = `<div class="ai-section"><h3>🤖 AI 分析</h3><div class="ai-result">${esc(text)}</div></div>`;
  } catch (e) {
    out.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

// ---------- Liuren ----------

async function renderLiuren(root) {
  root.innerHTML = `
    <h2 style="margin-bottom:14px;">📐 大六壬 · 堅六壬</h2>
    <p class="quote">「大六壬者，眾術之王，天人之學也。」</p>
    <div class="status-row">
      <span class="mode-badge auto" id="liuren-mode-badge">📐 時間盤</span>
      <span class="text-secondary text-small">依輸入時間自動推算節氣、農曆、干支</span>
    </div>

    <div class="liuren-tab">
      <aside>
        <div class="card">
          <h4 class="card-label">排盤資訊</h4>
          <div id="liuren-meta" class="mt-2 text-small text-secondary">排盤後顯示</div>
        </div>
      </aside>
      <div class="liuren-main">
        <div class="shipan-shell" id="liuren-shipan">
          <div class="loading-block"><div class="loading"></div></div>
        </div>
        <div class="section-title">月課 · 日課 · 時課</div>
        <div id="liuren-three"></div>
        <div id="liuren-shensha"></div>
        <div class="action-bar">
          <button class="btn btn-primary" id="liuren-run-btn">🔮 立即排盤</button>
          <button class="btn" id="liuren-ai-btn">🔍 AI 分析</button>
        </div>
        <div id="liuren-ai-result"></div>
      </div>
    </div>
  `;
  document.getElementById('liuren-run-btn').addEventListener('click', runLiuren);
  document.getElementById('liuren-ai-btn').addEventListener('click', aiAnalyzeLiuren);
  window.addEventListener('shushu:rerun', (e) => {
    if (e.detail.tab === 'liuren') runLiuren();
  });
  runLiuren();
}

let liurenState = { details: null, dayChart: null };

async function runLiuren() {
  const s = store.get();
  const wrap = document.getElementById('liuren-shipan');
  wrap.innerHTML = `<div class="loading-block"><div class="loading"></div></div>`;
  try {
    const result = await api.divination({
      system: 'liuren',
      method: 'datetime',
      datetime: datetimeISO(),
      timezone: s.timezone,
    });
    liurenState.details = result.details;
    liurenState.dayChart = result.details;  // for now 日課 is the main chart
    renderLiurenAll(result.details);
  } catch (e) {
    wrap.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

function renderLiurenAll(d) {
  // Meta
  const meta = [];
  if (d.ge_ju) meta.push(["格局", d.ge_ju.join("、")]);
  if (d.jieqi) meta.push(["節氣", d.jieqi]);
  if (d.lunar_month) meta.push(["農曆月", d.lunar_month]);
  if (d.ri_ma) meta.push(["日馬", d.ri_ma]);
  const metaHtml = meta.map(([k, v]) =>
    `<div class="meta-line"><span class="meta-label">${k}</span><span class="meta-value">${esc(v)}</span></div>`
  ).join("");
  document.getElementById("liuren-meta").innerHTML = metaHtml;

  // 式盤: center = 三傳四課 of 日課
  const center = renderCenterText(d.san_chuan, d.si_ke);
  // Active mansion: rough — pick first non-empty from 地轉天盤 mapped to 宿 (simplified)
  const activeMansion = "心";  // visual default; ideally compute from lunar day
  document.getElementById("liuren-shipan").innerHTML = renderShipan(d, activeMansion, center);

  // 月/日/時 - for now we only have 日課; show simplified version
  const day = d;
  const monthChart = synthesizeChart(d, "月");
  const hourChart = synthesizeChart(d, "時");
  document.getElementById("liuren-three").innerHTML = renderThreeCharts(monthChart, day, hourChart);

  // 神煞
  document.getElementById("liuren-shensha").innerHTML = renderLiurenShenSha(d);
}

function synthesizeChart(base, scope) {
  // For month/hour we don't have separate chart data from API; synthesize minimal
  // structure from the 日課 as a placeholder for the three-chart grid.
  return {
    "三傳": base.san_chuan,
    "四課": base.si_ke,
    "地轉天將": base["地轉天將"] || base.tian_di_pan?.["天將"]?.reduce
      ? base.tian_di_pan["天將"] : {},
    "地轉天盤": base["地轉天盤"] || {},
  };
}

async function aiAnalyzeLiuren() {
  if (!liurenState.details) return;
  const out = document.getElementById('liuren-ai-result');
  out.innerHTML = `<div class="ai-section"><div class="loading-block"><div class="loading"></div></div></div>`;
  try {
    const summary = JSON.stringify({
      jieqi: liurenState.details.jieqi,
      ge_ju: liurenState.details.ge_ju,
      san_chuan: liurenState.details.san_chuan,
      si_ke: liurenState.details.si_ke,
    }, null, 2);
    const text = await callAI([
      { role: 'system', content: '你是一位大六壬大師。請根據排盤資料進行簡明分析（300字內）。' },
      { role: 'user', content: `大六壬排盤：\n${summary}` },
    ]);
    out.innerHTML = `<div class="ai-section"><h3>🤖 AI 分析</h3><div class="ai-result">${esc(text)}</div></div>`;
  } catch (e) {
    out.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

// ---------- Qimen ----------

async function renderQimen(root) {
  root.innerHTML = `
    <h2 style="margin-bottom:14px;">⭐ 奇門遁甲 · 堅奇門</h2>
    <p class="quote">「奇門遁甲，演通萬類之機，貫穿天地之奧。」</p>
    <div class="status-row">
      <span class="mode-badge auto" id="qimen-mode-badge">📐 時家拆補</span>
      <select id="qimen-variant" style="background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border-subtle);border-radius:6px;padding:4px 8px;">
        <option value="chabu">時家拆補（預設）</option>
        <option value="zhirun">時家置閏</option>
        <option value="ke_chabu">刻家拆補</option>
        <option value="ke_zhirun">刻家置閏</option>
        <option value="jinhanyujing">金函玉鏡日家</option>
      </select>
    </div>

    <div class="qimen-tab">
      <aside>
        <div class="card">
          <h4 class="card-label">排盤資訊</h4>
          <div id="qimen-meta" class="mt-2 text-small text-secondary">排盤後顯示</div>
        </div>
        <div id="qimen-shensha"></div>
      </aside>
      <div class="qimen-main">
        <div class="qimen-grid-card" id="qimen-grid">
          <div class="loading-block"><div class="loading"></div></div>
        </div>
        <div class="qimen-legend">
          <span><span class="swatch" style="background:#FF4444"></span>火</span>
          <span><span class="swatch" style="background:#CD853F"></span>土</span>
          <span><span class="swatch" style="background:#4CAF50"></span>木</span>
          <span><span class="swatch" style="background:#4499FF"></span>水</span>
          <span><span class="swatch" style="background:#FFB800"></span>金</span>
          <span><span class="swatch" style="background:#FFD700"></span>馬星/空亡</span>
        </div>
        <div class="action-bar">
          <button class="btn btn-primary" id="qimen-run-btn">🔮 立即排盤</button>
          <button class="btn" id="qimen-ai-btn">🔍 AI 分析</button>
        </div>
        <div id="qimen-ai-result"></div>
      </div>
    </div>
  `;
  document.getElementById('qimen-run-btn').addEventListener('click', runQimen);
  document.getElementById('qimen-ai-btn').addEventListener('click', aiAnalyzeQimen);
  document.getElementById('qimen-variant').addEventListener('change', runQimen);
  window.addEventListener('shushu:rerun', (e) => {
    if (e.detail.tab === 'qimen') runQimen();
  });
  runQimen();
}

let qimenState = { details: null };

async function runQimen() {
  const s = store.get();
  const variant = document.getElementById('qimen-variant').value;
  const gridEl = document.getElementById('qimen-grid');
  gridEl.innerHTML = `<div class="loading-block"><div class="loading"></div></div>`;
  try {
    const result = await api.divination({
      system: 'qimen',
      method: 'datetime',
      datetime: datetimeISO(),
      timezone: s.timezone,
      details: { variant },
    });
    qimenState.details = result.details;
    gridEl.innerHTML = renderQimenGrid(result.details);
    document.getElementById('qimen-meta').innerHTML = renderQimenMeta(result.details);
    document.getElementById('qimen-shensha').innerHTML = renderQimenShenSha(result.details);
    const labels = { chabu: "時家拆補", zhirun: "時家置閏", ke_chabu: "刻家拆補", ke_zhirun: "刻家置閏", jinhanyujing: "金函玉鏡日家" };
    document.getElementById('qimen-mode-badge').textContent = `📐 ${labels[variant]}`;
  } catch (e) {
    gridEl.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

async function aiAnalyzeQimen() {
  if (!qimenState.details) return;
  const out = document.getElementById('qimen-ai-result');
  out.innerHTML = `<div class="ai-section"><div class="loading-block"><div class="loading"></div></div></div>`;
  try {
    const summary = JSON.stringify(qimenState.details, null, 2);
    const text = await callAI([
      { role: 'system', content: '你是一位奇門遁甲大師。請根據排盤資料進行簡明分析（300字內）。' },
      { role: 'user', content: `奇門遁甲排盤：\n${summary}` },
    ]);
    out.innerHTML = `<div class="ai-section"><h3>🤖 AI 分析</h3><div class="ai-result">${esc(text)}</div></div>`;
  } catch (e) {
    out.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

// ---------- Taiyi ----------

async function renderTaiyi(root) {
  root.innerHTML = `
    <h2 style="margin-bottom:14px;">🔥 太乙神數 · 堅太乙</h2>
    <p class="quote">「太乙者，天地之神也。算歷紀，觀氣運，斷人間之休咎。」</p>
    <div class="status-row">
      <span class="mode-badge auto" id="taiyi-mode-badge">🔥 分計 · 太乙統宗</span>
      <select id="taiyi-scope" style="background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border-subtle);border-radius:6px;padding:4px 8px;">
        <option value="fenji">分計（預設）</option>
        <option value="shiji">時計</option>
        <option value="riji">日計</option>
        <option value="yueji">月計</option>
        <option value="nianji">年計</option>
      </select>
      <select id="taiyi-formula" style="background:var(--bg-input);color:var(--text-primary);border:1px solid var(--border-subtle);border-radius:6px;padding:4px 8px;">
        <option value="tongzong">太乙統宗（預設）</option>
        <option value="jinjing">太乙金鏡</option>
        <option value="taojinge">太乙淘金歌</option>
        <option value="ju">太乙局</option>
      </select>
    </div>

    <div class="taiyi-tab">
      <aside>
        <div class="card">
          <h4 class="card-label">關於太乙神數</h4>
          <p class="text-small text-secondary mt-1">
            太乙統稱「三式之末」，分年/月/日/時/分五種計法。
            本系統預設使用分計（最精細），可依需求切換。
          </p>
        </div>
      </aside>
      <div class="taiyi-main">
        <div id="taiyi-dashboard">
          <div class="loading-block"><div class="loading"></div></div>
        </div>
        <div class="action-bar">
          <button class="btn btn-primary" id="taiyi-run-btn">🔮 立即排盤</button>
          <button class="btn" id="taiyi-ai-btn">🔍 AI 分析</button>
        </div>
        <div id="taiyi-ai-result"></div>
      </div>
    </div>
  `;
  document.getElementById('taiyi-run-btn').addEventListener('click', runTaiyi);
  document.getElementById('taiyi-ai-btn').addEventListener('click', aiAnalyzeTaiyi);
  document.getElementById('taiyi-scope').addEventListener('change', runTaiyi);
  document.getElementById('taiyi-formula').addEventListener('change', runTaiyi);
  window.addEventListener('shushu:rerun', (e) => {
    if (e.detail.tab === 'taiyi') runTaiyi();
  });
  runTaiyi();
}

let taiyiState = { details: null };

async function runTaiyi() {
  const s = store.get();
  const scope = document.getElementById('taiyi-scope').value;
  const formula = document.getElementById('taiyi-formula').value;
  const dashEl = document.getElementById('taiyi-dashboard');
  dashEl.innerHTML = `<div class="loading-block"><div class="loading"></div></div>`;
  try {
    const result = await api.divination({
      system: 'taiyi',
      method: 'datetime',
      datetime: datetimeISO(),
      timezone: s.timezone,
      details: { scope, formula },
    });
    taiyiState.details = result.details;
    dashEl.innerHTML = renderTaiyiDashboard(result);
    const scopeLabel = { fenji: "分計", shiji: "時計", riji: "日計", yueji: "月計", nianji: "年計" };
    const formulaLabel = { tongzong: "太乙統宗", jinjing: "太乙金鏡", taojinge: "太乙淘金歌", ju: "太乙局" };
    document.getElementById('taiyi-mode-badge').textContent =
      `🔥 ${scopeLabel[scope]} · ${formulaLabel[formula]}`;
  } catch (e) {
    dashEl.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

async function aiAnalyzeTaiyi() {
  if (!taiyiState.details) return;
  const out = document.getElementById('taiyi-ai-result');
  out.innerHTML = `<div class="ai-section"><div class="loading-block"><div class="loading"></div></div></div>`;
  try {
    const summary = JSON.stringify(taiyiState.details, null, 2);
    const text = await callAI([
      { role: 'system', content: '你是一位太乙神數大師。請根據排盤資料進行簡明分析（300字內）。' },
      { role: 'user', content: `太乙神數排盤：\n${summary}` },
    ]);
    out.innerHTML = `<div class="ai-section"><h3>🤖 AI 分析</h3><div class="ai-result">${esc(text)}</div></div>`;
  } catch (e) {
    out.innerHTML = `<div class="error-block">❌ ${esc(e.message)}</div>`;
  }
}

// ===================== AI helper (mock or real) =====================

async function callAI(messages) {
  const ai = store.get().ai || {};
  if (ai.provider === "mock" || !ai.apiKey) {
    // Mock AI: synthesize a reasonable-looking summary
    return mockAIResponse(messages);
  }
  return realAI(messages);
}

function mockAIResponse(messages) {
  const user = messages[messages.length - 1].content;
  // Trivial mock: extract a few keywords, produce a generic summary
  const sample = user.slice(0, 600).split("\n").slice(0, 8).join("\n");
  return `【mock AI】這是開發環境的占位回應。\n\n以下是排盤摘錄：\n${sample}\n\n（請在「🔧 AI 設定」填入 Cerebras 或 OpenAI 相容 API Key 以啟用真實分析。）`;
}

async function realAI(messages) {
  const ai = store.get().ai;
  return aiModule.complete({
    messages,
    provider: ai.provider,
    apiKey: ai.apiKey,
    server: ai.server,
    model: ai.model,
    temperature: ai.temperature || 0.7,
    maxTokens: ai.maxTokens || 2000,
  });
}

import * as aiModule from "./api.js";

// ===================== Settings modal =====================

function openSettings() {
  const ai = store.get().ai;
  const html = `
    <label>AI 提供者</label>
    <select id="ai-provider">
      <option value="mock" ${ai.provider === 'mock' ? 'selected' : ''}>Mock（開發）</option>
      <option value="cerebras" ${ai.provider === 'cerebras' ? 'selected' : ''}>Cerebras</option>
      <option value="openai_compat" ${ai.provider === 'openai_compat' ? 'selected' : ''}>OpenAI 相容</option>
    </select>
    <label>API Key</label>
    <input type="password" id="ai-key" value="${esc(ai.apiKey || '')}" placeholder="sk-..." />
    <label>Server URL（OpenAI 相容模式才需填）</label>
    <input type="text" id="ai-server" value="${esc(ai.server || '')}" placeholder="https://api.openai.com/v1" />
    <label>模型名稱</label>
    <input type="text" id="ai-model" value="${esc(ai.model || '')}" placeholder="gpt-4o-mini / qwen-plus / claude-3-5-sonnet" />
    <label>系統提示</label>
    <textarea id="ai-system">${esc(ai.systemPrompt || '')}</textarea>
    <label>Temperature（0 = 精確，1.5 = 創造）</label>
    <input type="number" id="ai-temperature" min="0" max="1.5" step="0.05" value="${ai.temperature || 0.7}" />
    <label>Max Tokens</label>
    <input type="number" id="ai-max-tokens" min="256" max="32000" value="${ai.maxTokens || 2000}" />
  `;
  document.getElementById("settings-content").innerHTML = html;
  document.getElementById("settings-modal").style.display = "flex";
}

function closeSettings() {
  document.getElementById("settings-modal").style.display = "none";
}

function saveSettings() {
  store.setAi({
    provider: document.getElementById("ai-provider").value,
    apiKey: document.getElementById("ai-key").value,
    server: document.getElementById("ai-server").value,
    model: document.getElementById("ai-model").value,
    systemPrompt: document.getElementById("ai-system").value,
    temperature: parseFloat(document.getElementById("ai-temperature").value),
    maxTokens: parseInt(document.getElementById("ai-max-tokens").value),
  });
  closeSettings();
}

document.addEventListener("click", (e) => {
  if (e.target.dataset.action === "open-settings") openSettings();
  if (e.target.dataset.action === "close-settings") closeSettings();
  if (e.target.dataset.action === "reset-state") {
    if (confirm("確定重置所有狀態？")) {
      store.reset();
      location.reload();
    }
  }
});

// Click backdrop to close modal
document.getElementById("settings-modal").addEventListener("click", (e) => {
  if (e.target.id === "settings-modal") closeSettings();
});

// Save before close
const origCloseSettings = closeSettings;
closeSettings = function() {
  saveSettings();
  origCloseSettings();
};

// ===================== Init =====================

bindTopbar();
switchTab(currentTab());

// Save settings when leaving
window.addEventListener("beforeunload", saveSettings);