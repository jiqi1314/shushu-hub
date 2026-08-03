# Architecture · 架構

[English](#english) · [繁體中文](#繁體中文)

---

<a id="english"></a>
## 🇬🇧 English

### High-Level Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend: Next.js 14 + TypeScript + Tailwind + shadcn/ui    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Unified Input Page  │  Comparison View  │  AI Summary│  │
│  └────────────────────────────────────────────────────────┘  │
│  i18n: 繁中 / 簡中 / English                                 │
│  Local history: localStorage (no backend persistence)         │
└──────────────────────────┬───────────────────────────────────┘
                           │ REST + JSON
┌──────────────────────────▼───────────────────────────────────┐
│  Backend: FastAPI (Python 3.11)                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  /api/divination (POST) — unified reading              │  │
│  │  /api/compare      (POST) — cross-system field mapping │  │
│  │  /api/interpret    (POST) — AI synthesis               │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Module Adapters (Adapter Pattern)                     │  │
│  │  ├─ IchingShifaAdapter  (周易)                         │  │
│  │  ├─ LiuRenAdapter       (大六壬)                       │  │
│  │  ├─ QiMenAdapter        (奇門遁甲)                     │  │
│  │  ├─ TaiYiAdapter        (太乙神數)                     │  │
│  │  └─ AstroAdapter        (88 占星)                      │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Core Services                                         │  │
│  │  ├─ ganzhi (干支)                                      │  │
│  │  ├─ lunar (農曆)                                       │  │
│  │  ├─ true_solar (真太陽時, opt-in)                     │  │
│  │  ├─ solar_term (節氣)                                  │  │
│  │  ├─ field_mapper (跨系統欄位標準化)                   │  │
│  │  └─ cerebras_client (AI, mock-first)                  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │ pip install
┌──────────────────────────▼───────────────────────────────────┐
│  kentang2017 Open Source Libraries                           │
│  ichingshifa · kinliuren · kinqimen · kintaiyi · kinastro    │
└──────────────────────────────────────────────────────────────┘
```

### Unified Input Schema

The single input form collects:

| Field | Required | Description |
|-------|----------|-------------|
| `datetime` | ✅ | ISO 8601 datetime in user's timezone |
| `timezone` | ✅ | IANA timezone name |
| `method` | ✅ | `random` / `datetime` / `manual` |
| `question` | optional | Free-text query context |
| `location` | optional | City name / lat+lon (for astrology) |
| `gender` | optional | `male` / `female` (for some systems) |
| `use_true_solar_time` | optional | Default `false`; opt-in correction |

### Unified Output Schema

```python
class DivinationResult(BaseModel):
    system_id: str            # "ichingshifa"
    system_name: str          # "周易筮法"
    ganzhi: GanzhiInfo        # 干支四柱
    five_elements: list[str]  # 五行
    main_judgment: str        # 主要判斷
    favorable: list[str]      # 吉神/方位/顏色
    unfavorable: list[str]    # 凶神/避忌
    details: dict[str, Any]   # 系統專屬細節
    raw_output: str           # 原始排盤文字
    computed_at: datetime     # 計算時間
```

### Module Adapter Pattern

Every shushu system is wrapped in an adapter implementing:

```python
class BaseModule(ABC):
    system_id: str
    system_name: str

    @abstractmethod
    def compute(self, request: DivinationRequest) -> DivinationResult: ...
```

This lets new systems be added without touching the API layer.

### i18n Error Handling

Errors return:

```json
{
  "error_code": "INVALID_DATETIME",
  "message": "Invalid datetime format. Use ISO 8601.",
  "details": { "received": "2026-08-04 14:30" }
}
```

Frontend uses `error_code` to look up localized message in its i18n catalog.

---

<a id="繁體中文"></a>
## 🇹🇼 繁體中文

### 整體架構圖

（見上方英文版圖表）

### 統一輸入欄位

| 欄位 | 必填 | 說明 |
|------|------|------|
| `datetime` | ✅ | ISO 8601 時間（含時區）|
| `timezone` | ✅ | IANA 時區名稱 |
| `method` | ✅ | `random` / `datetime` / `manual` |
| `question` | 選填 | 問事描述 |
| `location` | 選填 | 城市名稱或經緯度 |
| `gender` | 選填 | `male` / `female` |
| `use_true_solar_time` | 選填 | 預設 `false`，由使用者勾選啟用 |

### 統一輸出模型

每套系統都回傳標準化的 `DivinationResult`，包含 干支、五行、吉凶、原始排盤 等共用欄位。

### 模組化設計

使用 Adapter Pattern，每套術數都實作 `BaseModule.compute(request) -> DivinationResult`。新增術數只需新增 adapter，無須更動 API 層。

### i18n 錯誤處理

錯誤一律以 `error_code`（英文字串常數）回傳，前端依此代碼查找對應語系的錯誤訊息。後端訊息僅作 fallback 用途。