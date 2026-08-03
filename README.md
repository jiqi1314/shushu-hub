# 🔮 shushu-hub · 術數整合平台

> **Single input, multiple divination systems, side-by-side comparison.**

[English](#english) · [繁體中文](#繁體中文) · [简体中文](#简体中文)

---

<a id="english"></a>
## 🇬🇧 English

**shushu-hub** is an open-source web application that unifies the major Chinese and cross-cultural **shushu (術數)** divination systems into a single platform. Enter your birth details or a question once, and receive side-by-side readings from multiple systems — highlighting their overlaps, divergences, and combined insight.

### Why shushu-hub?

The Chinese metaphysical tradition includes dozens of mature divination systems — I-Ching (周易), Da Liu Ren (大六壬), Qi Men Dun Jia (奇門遁甲), Tai Yi (太乙), Zi Wei Dou Shu (紫微斗數), Ba Zi (八字), and many more. Each system has its own input format, vocabulary, and interpretive framework, making cross-comparison difficult.

**shushu-hub** solves this by:

1. Providing a **unified input form** (date, time, location, question)
2. Computing results across multiple systems in parallel
3. Normalizing outputs into a **shared data model**
4. Presenting side-by-side panels with **common fields highlighted**
5. Optionally invoking **AI synthesis** to summarize consensus and contradictions

### Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic v2
- **Frontend**: Next.js 14, TypeScript, Tailwind, shadcn/ui (planned)
- **AI**: Cerebras (with mock fallback for development)
- **i18n**: 繁體中文 / 简体中文 / English

### Status

🚧 **Phase 2 (三式 + 並排比較)** — `main` branch
- ✅ FastAPI app + health endpoint
- ✅ ichingshifa (周易) module adapter
- ✅ liuren (大六壬) module adapter
- ✅ qimen (奇門遁甲) module adapter
- ✅ taiyi (太乙神數) module adapter
- ✅ `POST /api/compare` 多系統並排比較端點 (Phase 2 ✓)
- ✅ `field_mapper.py` 跨系統語意標準化
- ✅ Unified request/response schema
- ✅ i18n-friendly error handling
- 🔜 Astro module (88 systems via kinastro)
- 🔜 Next.js frontend

### Quick Start (Backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

### Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

### Acknowledgements

Built on the open-source libraries of [kentang2017](https://github.com/kentang2017):

- [ichingshifa](https://github.com/kentang2017/ichingshifa) · 周易筮法
- [kinliuren](https://github.com/kentang2017/kinliuren) · 大六壬
- [kinqimen](https://github.com/kentang2017/kinqimen) · 奇門遁甲
- [kintaiyi](https://github.com/kentang2017/kintaiyi) · 太乙神數
- [kinastro](https://github.com/kentang2017/kinastro) · 88 占星系統

### License

MIT — see [`LICENSE`](LICENSE).

---

<a id="繁體中文"></a>
## 🇹🇼 繁體中文

**shushu-hub** 是一個開源 Web 應用程式，將主要的術數系統整合到單一平台。只需輸入一次資料（時辰、地點、問題），即可同時獲得多套系統的排盤結果，並以並排方式比較，凸顯其重疊、相異與綜合洞見。

### 為什麼需要 shushu-hub？

中國傳統術數包含數十種成熟的占卜體系——周易、大六壬、奇門遁甲、太乙神數、紫微斗數、八字等等。每套系統各有其輸入格式、術語與解讀框架，跨系統比較非常困難。

**shushu-hub** 的解法：

1. **統一輸入表單**（日期、時間、地點、問題）
2. 平行計算多套系統結果
3. 將輸出**標準化為共用資料模型**
4. **並排顯示面板**，高亮共通欄位
5. 可選地呼叫 **AI 綜合解讀**，彙整共識與矛盾

### 技術棧

- **後端**：Python 3.11、FastAPI、Pydantic v2
- **前端**：Next.js 14、TypeScript、Tailwind、shadcn/ui（規劃中）
- **AI**：Cerebras（開發階段使用 mock）
- **多語系**：繁體中文 / 简体中文 / English

### 狀態

🚧 **第一階段（後端骨架）** — `main` 分支
- ✅ FastAPI app + 健康檢查端點
- ✅ ichingshifa（周易）模組 adapter
- ✅ 統一請求/回應 schema
- ✅ i18n 友善的錯誤處理
- 🔜 大六壬、奇門、太乙模組
- 🔜 占星模組（透過 kinastro 整合 88 系統）
- 🔜 Next.js 前端

### 快速啟動（後端）

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

造訪 `http://localhost:8000/docs` 查看互動式 API 文件。

### 致謝

基於 [kentang2017](https://github.com/kentang2017) 的開源套件構建：

- [ichingshifa](https://github.com/kentang2017/ichingshifa) · 周易筮法
- [kinliuren](https://github.com/kentang2017/kinliuren) · 大六壬
- [kinqimen](https://github.com/kentang2017/kinqimen) · 奇門遁甲
- [kintaiyi](https://github.com/kentang2017/kintaiyi) · 太乙神數
- [kinastro](https://github.com/kentang2017/kinastro) · 88 占星系統

### 授權

MIT — 詳見 [`LICENSE`](LICENSE)。

---

<a id="简体中文"></a>
## 🇨🇳 简体中文

**shushu-hub** 是一个开源 Web 应用程式，将主要的术数系统整合到单一平台。只需输入一次资料（时辰、地点、问题），即可同时获得多套系统的排盘结果，并以并排方式比较，凸显其重叠、相异与综合洞见。

### 为什么需要 shushu-hub？

中国传统术数包含数十种成熟的占卜体系——周易、大六壬、奇门遁甲、太乙神数、紫微斗数、八字等等。每套系统各有其输入格式、术语与解读框架，跨系统比较非常困难。

**shushu-hub** 的解法：

1. **统一输入表单**（日期、时间、地点、问题）
2. 平行计算多套系统结果
3. 将输出**标准化为共用资料模型**
4. **并排显示面板**，高亮共通栏位
5. 可选地呼叫 **AI 综合解读**，汇整共识与矛盾

### 技术栈

- **后端**：Python 3.11、FastAPI、Pydantic v2
- **前端**：Next.js 14、TypeScript、Tailwind、shadcn/ui（规划中）
- **AI**：Cerebras（开发阶段使用 mock）
- **多语言**：繁体中文 / 简体中文 / English

### 状态

🚧 **第一阶段（后端骨架）** — `main` 分支
- ✅ FastAPI app + 健康检查端点
- ✅ ichingshifa（周易）模组 adapter
- ✅ 统一请求/回应 schema
- ✅ i18n 友善的错误处理
- 🔜 大六壬、奇门、太乙模组
- 🔜 占星模组（透过 kinastro 整合 88 系统）
- 🔜 Next.js 前端

### 快速启动（后端）

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

访问 `http://localhost:8000/docs` 查看互动式 API 文件。

### 致谢

基于 [kentang2017](https://github.com/kentang2017) 的开源套件构建：

- [ichingshifa](https://github.com/kentang2017/ichingshifa) · 周易筮法
- [kinliuren](https://github.com/kentang2017/kinliuren) · 大六壬
- [kinqimen](https://github.com/kentang2017/kinqimen) · 奇门遁甲
- [kintaiyi](https://github.com/kentang2017/kintaiyi) · 太乙神数
- [kinastro](https://github.com/kentang2017/kinastro) · 88 占星系统

### 授权

MIT — 详见 [`LICENSE`](LICENSE)。