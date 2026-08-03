/**
 * API client for shushu-hub FastAPI backend.
 * All requests go through this module so we have one place for error
 * handling and request shape.
 */

const BASE = ""; // same-origin (FastAPI serves both UI and API)

async function request(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  let data;
  try { data = await res.json(); } catch { data = null; }
  if (!res.ok) {
    const msg = data?.detail?.message || data?.detail?.error_code
      || `HTTP ${res.status}`;
    const code = data?.detail?.error_code || "UNKNOWN";
    throw Object.assign(new Error(msg), { status: res.status, code });
  }
  return data;
}

export const api = {
  async compare({ datetime, timezone, question, latitude, longitude,
                  use_true_solar_time, systems, per_system }) {
    return request("/api/compare", {
      datetime,
      timezone,
      question: question || undefined,
      latitude,
      longitude,
      use_true_solar_time: !!use_true_solar_time,
      systems,           // optional — undefined = all
      per_system: per_system || {},
    });
  },

  async divination(req) {
    return request("/api/divination", req);
  },

  async systems() {
    const res = await fetch(`${BASE}/api/systems`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};

/**
 * AI integration. Calls Cerebras (default) or any OpenAI-compatible
 * endpoint. Cerebras and OpenAI both use the same chat completions
 * schema, so one fetch path works for both.
 */
export const ai = {
  async complete({ messages, provider, apiKey, server, model,
                   temperature = 0.7, maxTokens = 2000 }) {
    if (provider === "cerebras") {
      const base = "https://api.cerebras.ai/v1";
      return chatCompletion({ base, apiKey, model, messages,
                             temperature, maxTokens });
    }
    // OpenAI-compatible
    return chatCompletion({ base: server || "https://api.openai.com/v1",
                            apiKey, model, messages,
                            temperature, maxTokens });
  },
};

async function chatCompletion({ base, apiKey, model, messages,
                                temperature, maxTokens }) {
  if (!apiKey) throw new Error("請輸入 API Key");
  if (!model) throw new Error("請選擇模型");
  const url = base.replace(/\/$/, "") + "/chat/completions";
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      messages,
      temperature,
      max_tokens: maxTokens,
    }),
  });
  const data = await res.json();
  if (!res.ok) {
    const msg = data?.error?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  const content = data?.choices?.[0]?.message?.content;
  if (!content) throw new Error("AI 未返回內容");
  return content;
}