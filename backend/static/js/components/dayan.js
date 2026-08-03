/**
 * 大衍筮法 state machine (六爻 interactive divination).
 * Mirrors kentang's ichingshifa/app.py `render_dayan_tab()` logic.
 *
 * State:
 *   phase: 'idle' | 'active' | 'completed'
 *   yao:   1..6 (current line being cast, bottom-up)
 *   change: 1..3 (current change within a line)
 *   step: 'divide' | 'hang_one' | 'count_four' | 'change_done' | 'yao_done'
 *   stalks: 49 (current pile, decreases by removed sum)
 *   lines: string[] (collected 6/7/8/9 values, bottom-up)
 *
 * Per-line: 3 changes, each subtracts (left_rem + right_rem + hung).
 * Final:  (49 - total_removed) / 4 = yao value.
 */

const YAO_LABEL = { "6": "老陰", "7": "少陽", "8": "少陰", "9": "老陽" };
const YAO_SYMBOL = { "6": "⚋×", "7": "⚊", "8": "⚋", "9": "⚊○" };

export function createDayanState() {
  return {
    phase: "idle",
    yao: 0,
    change: 0,
    step: "ready",
    stalks: 49,
    lines: [],
    changesData: [],
    left: 24,
    right: 25,
    hung: 0,
    left_rem: 0,
    right_rem: 0,
    removed: 0,
    combine: "",
  };
}

function randomSplit(n) {
  // Pick a random split between roughly 1/3 and 2/3 of n.
  const lo = Math.max(1, Math.floor(n / 3));
  const hi = Math.max(lo + 1, Math.floor((n * 2) / 3));
  const left = Math.floor(Math.random() * (hi - lo + 1)) + lo;
  return [left, n - left];
}

function remainderFour(n) {
  const r = n % 4;
  return r === 0 ? 4 : r;
}

export function dayanStart(state) {
  state.phase = "active";
  state.yao = 1;
  state.change = 1;
  state.step = "divide";
  state.stalks = 49;
  state.changesData = [];
  [state.left, state.right] = randomSplit(49);
  state.hung = 0;
  return state;
}

export function dayanDivide(state) {
  // Re-pick the split randomly (user can re-roll)
  [state.left, state.right] = randomSplit(state.stalks);
  state.step = "hang_one";
  return state;
}

export function dayanHangOne(state) {
  if (state.right >= 1) {
    state.hung = 1;
    state.right -= 1;
  }
  state.step = "count_four";
  return state;
}

export function dayanCountFour(state) {
  const left_rem = remainderFour(state.left);
  const right_rem = remainderFour(state.right);
  state.left_rem = left_rem;
  state.right_rem = right_rem;
  state.removed = left_rem + right_rem + state.hung;
  state.changesData.push({
    change: state.change,
    left: state.left,
    right: state.right,
    hung: state.hung,
    left_rem: left_rem,
    right_rem: right_rem,
    removed: state.removed,
  });
  state.step = "change_done";
  return state;
}

export function dayanAdvance(state) {
  if (state.change < 3) {
    const removedSoFar = state.changesData.reduce((s, c) => s + c.removed, 0);
    state.stalks = 49 - removedSoFar;
    state.change += 1;
    state.step = "divide";
    [state.left, state.right] = randomSplit(state.stalks);
    state.hung = 0;
  } else {
    const total_removed = state.changesData.reduce((s, c) => s + c.removed, 0);
    const remaining = 49 - total_removed;
    state.lines.push(String(Math.floor(remaining / 4)));
    state.step = "yao_done";
    if (state.lines.length >= 6) {
      state.phase = "completed";
      state.combine = state.lines.join("");
    }
  }
  return state;
}

export function dayanStartNextYao(state) {
  state.yao = state.yao + 1;
  return dayanStart(state);
}

export function dayanReset() {
  return createDayanState();
}

/**
 * Render the dayan scene — the current 變 step visualization.
 */
export function renderDayanScene(state) {
  const phaseLabel = {
    divide: `第${state.yao}爻 · 第${state.change}變 · 分而為二以象兩`,
    hang_one: `第${state.yao}爻 · 第${state.change}變 · 掛一以象三`,
    count_four: `第${state.yao}爻 · 第${state.change}變 · 揲之以四`,
    change_done: `第${state.change}變　歸奇 ${state.removed} 策`,
    yao_done: `第 ${state.yao} 爻　${YAO_LABEL[state.lines[state.lines.length - 1]]}`,
    ready: "準備起卦",
  }[state.step];

  if (state.step === "divide" || state.step === "ready") {
    return `
      <div class="dayan-scene">
        <div class="dayan-phase">${phaseLabel}</div>
        <div class="dayan-piles">
          <div class="dayan-pile">
            <div class="dayan-pile-num">${state.left}</div>
            <div class="dayan-pile-tag">左堆</div>
          </div>
          <div class="dayan-pile">
            <div class="dayan-pile-num">${state.right}</div>
            <div class="dayan-pile-tag">右堆</div>
          </div>
        </div>
        <div class="dayan-total">分而為二以象兩 · 共 ${state.stalks} 策</div>
      </div>
    `;
  }
  if (state.step === "hang_one") {
    return `
      <div class="dayan-scene">
        <div class="dayan-phase">${phaseLabel}</div>
        <div class="dayan-piles">
          <div class="dayan-pile">
            <div class="dayan-pile-num">${state.left}</div>
            <div class="dayan-pile-tag">左堆</div>
          </div>
          <div class="dayan-pile">
            <div class="dayan-pile-num">${state.right}</div>
            <div class="dayan-pile-tag">右堆</div>
          </div>
        </div>
        ${state.hung ? `<div class="dayan-hung">掛一 · ${state.hung}</div>` : ""}
      </div>
    `;
  }
  if (state.step === "count_four") {
    const lg = Math.floor(state.left / 4);
    const lr = state.left % 4;
    const rg = Math.floor(state.right / 4);
    const rr = state.right % 4;
    return `
      <div class="dayan-scene">
        <div class="dayan-phase">${phaseLabel}</div>
        <div class="dayan-count-row">
          <div class="dayan-count-item">
            <div class="dayan-count-num">${state.left}</div>
            <div class="dayan-count-tag">左堆</div>
          </div>
          <div class="dayan-count-item">
            <div class="dayan-count-num">${state.right}</div>
            <div class="dayan-count-tag">右堆</div>
          </div>
        </div>
        <div class="dayan-detail">左 ${state.left} → ${lg}×4+${lr || 4}　·　右 ${state.right} → ${rg}×4+${rr || 4}</div>
        ${state.hung ? `<div class="dayan-hung">掛一 · ${state.hung}</div>` : ""}
      </div>
    `;
  }
  if (state.step === "change_done") {
    return `
      <div class="dayan-scene">
        <div class="dayan-phase">${phaseLabel}</div>
        <div class="dayan-hung">第 ${state.change} 變：${state.left_rem} + ${state.right_rem} + ${state.hung} = ${state.removed} 策歸奇</div>
      </div>
    `;
  }
  if (state.step === "yao_done") {
    const last = state.lines[state.lines.length - 1];
    return `
      <div class="dayan-scene">
        <div class="dayan-phase">${phaseLabel}</div>
        <div class="dayan-result">
          <div class="dayan-result-num">${last}</div>
          <div class="dayan-result-tag">${YAO_LABEL[last]} · ${YAO_SYMBOL[last]}</div>
        </div>
      </div>
    `;
  }
  return "";
}

/** Render the progress panel showing 爻 / 變 / 已成. */
export function renderDayanProgress(state) {
  const steps = [
    { key: "分堆", label: "分而為二" },
    { key: "掛一", label: "掛一以象三" },
    { key: "揲四", label: "揲之以四" },
    { key: "歸奇", label: "歸奇於扐" },
    { key: "成爻", label: "成爻" },
  ];
  const stepKeys = ["divide", "hang_one", "count_four", "change_done", "yao_done"];
  const curStepIdx = stepKeys.indexOf(state.step);

  let pipeHtml = "";
  for (let i = 0; i < steps.length; i++) {
    let cls = "";
    if (state.phase === "active") {
      if (i < curStepIdx) cls = "done";
      else if (i === curStepIdx) cls = "active";
    }
    pipeHtml += `<div class="dyan-pipe-step ${cls}">${steps[i].key}</div>`;
  }

  return `
    <div class="dayan-progress">
      <h4>大衍筮法</h4>
      <div class="dayan-stats">
        <div class="dayan-stat"><div class="dayan-stat-v">${state.yao}</div><div class="dayan-stat-l">爻 / 6</div></div>
        <div class="dayan-stat"><div class="dayan-stat-v">${state.change}</div><div class="dayan-stat-l">變 / 3</div></div>
        <div class="dayan-stat"><div class="dayan-stat-v">${state.lines.length}</div><div class="dayan-stat-l">已成</div></div>
      </div>
      ${state.phase === "active" ? `<div class="dyan-pipeline">${pipeHtml}</div>` : ""}
      ${state.phase === "completed" ?
        `<div class="dyan-quote">大衍之數五十，其用四十有九。<br/>六爻已定，得以本卦${state.combine}起盤。</div>` :
        `<div class="dyan-quote">大衍之數五十，其用四十有九。</div>`
      }
    </div>
  `;
}