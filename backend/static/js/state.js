/**
 * Shared client-side state with localStorage persistence.
 * - topbar inputs (date/time/timezone/question) shared across all tabs
 * - AI settings persisted
 * - per-system state (e.g. dayan steps, manual lines) lives in tab modules
 */

const KEY = "shushu-hub.state.v1";

const DEFAULT_STATE = {
  // Top-bar shared input
  date: todayISO(),
  time: "14:30",
  timezone: "Asia/Hong_Kong",
  question: "",
  use_true_solar_time: false,
  latitude: null,
  longitude: null,

  // AI settings
  ai: {
    provider: "mock", // mock | cerebras | openai_compat
    apiKey: "",
    server: "",
    model: "",
    systemPrompt: "",
    temperature: 0.7,
    maxTokens: 2000,
  },
};

function todayISO() {
  const d = new Date();
  const pad = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

let state = load();

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...DEFAULT_STATE };
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_STATE, ...parsed,
             ai: { ...DEFAULT_STATE.ai, ...(parsed.ai || {}) } };
  } catch {
    return { ...DEFAULT_STATE };
  }
}

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch {}
}

export const store = {
  get() { return state; },
  set(patch) {
    state = { ...state, ...patch };
    save();
    notify();
  },
  setAi(patch) {
    state.ai = { ...state.ai, ...patch };
    save();
    notify();
  },
  reset() {
    state = { ...DEFAULT_STATE };
    save();
    notify();
  },
};

const listeners = new Set();
export function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
function notify() { listeners.forEach(fn => fn(state)); }

export function datetimeISO() {
  return `${state.date}T${state.time}:00`;
}