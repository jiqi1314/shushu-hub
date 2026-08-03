# Roadmap · 開發時程

## Phase 1 — Backend Skeleton ✅ (in progress)

**目標**：建立 repo + FastAPI 服務 + 第一個術數（ichingshifa）端點可運作

| 任務 | 狀態 |
|------|------|
| Repo + remote | ✅ |
| README / LICENSE / .gitignore | ✅ |
| Backend 骨架 (FastAPI + CORS) | 🔜 |
| Core: ganzhi / lunar / true_solar / solar_term | 🔜 |
| Schemas: DivinationRequest / Result / ErrorResponse | 🔜 |
| ichingshifa module adapter | 🔜 |
| `POST /api/divination` 端點 | 🔜 |
| `GET /health` 端點 | 🔜 |
| pytest 基本測試 | 🔜 |
| Dockerfile | 🔜 |
| 推送第一個 commit | 🔜 |

---

## Phase 2 — 三式其餘 + 並排比較（2 週）

| 任務 | 說明 |
|------|------|
| LiuRen adapter | 大六壬 |
| QiMen adapter | 奇門遁甲（時家 + 金函玉鏡）|
| TaiYi adapter | 太乙神數 |
| `POST /api/compare` | 跨系統欄位比對端點 |
| `field_mapper.py` | 抽出共通欄位 |

---

## Phase 3 — kinastro 整合（1.5 週）

| 任務 | 說明 |
|------|------|
| Astro adapter | 包裝 kinastro 88 系統 |
| 子系統選單 | 西洋/紫微/印度/亞洲… |
| 經緯度需求提示 | 必填時前端顯示提示 |

---

## Phase 4 — AI 綜合解讀（1 週）

| 任務 | 說明 |
|------|------|
| Cerebras client | 開發階段使用 mock 模式 |
| Prompt 模板 | 多系統彙整 prompt |
| `POST /api/interpret` | AI 解讀端點 |
| 結構化輸出 | JSON schema 驗證 |

---

## Phase 5 — Next.js 前端骨架（2 週）

| 任務 | 說明 |
|------|------|
| Next.js 14 + Tailwind + shadcn/ui | 基礎框架 |
| 統一輸入頁 | 日期/時間/地點/問題 |
| 並排比較頁 | 5 個系統並排卡片 |
| i18n (next-intl) | 繁中 / 簡中 / English |
| 響應式設計 | 桌面 + 行動裝置 |

---

## Phase 6 — 匯出 + 部署 + 文檔（1 週）

| 任務 | 說明 |
|------|------|
| PDF 匯出 | jsPDF / reportlab |
| JSON 匯出 | 完整原始資料 |
| 本地歷史 | localStorage |
| Vercel + Railway 部署 | CI/CD |
| API 文件 | Swagger UI（自動） |
| 使用者指南 | 各術數背景介紹 |

---

## 不在 MVP 範圍（未來擴充）

- 用戶帳號系統、雲端儲存
- iOS / Android 原生 App
- 問事記錄搜尋與標籤
- 賽馬、運動、金融占星整合
- 多使用者協作
- 付費進階解讀