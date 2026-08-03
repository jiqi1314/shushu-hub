# API Reference · API 文件

> 完整互動式文件：`http://localhost:8000/docs`（啟動後端後造訪）

---

## Endpoints

### `GET /health`

健康檢查。

**Response 200**
```json
{ "status": "ok", "version": "0.1.0" }
```

---

### `POST /api/divination`

執行單一術數排盤。

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `system` | `string` | ✅ | `"ichingshifa"` / `"liuren"` / `"qimen"` / `"taiyi"` (Phase 2) |
| `method` | `string` | ✅ | `"random"` / `"datetime"` / `"manual"` (system-dependent) |
| `details.variant` | `string` | optional | For `qimen`: `"chabu"` (default), `"zhirun"`, `"ke_chabu"`, `"ke_zhirun"`, `"jinhanyujing"` |
| `details.scope` | `string` | optional | For `taiyi`: `"fenji"` (分計, default), `"nianji"`, `"yueji"`, `"riji"`, `"shiji"` |
| `details.formula` | `string` | optional | For `taiyi`: `"tongzong"` (太乙統宗, default), `"jinjing"`, `"taojinge"`, `"ju"` |
| `datetime` | `string` (ISO 8601) | conditional | `method=datetime` 或 `method=manual` 時填寫 |
| `timezone` | `string` | conditional | IANA 時區名稱，如 `"Asia/Hong_Kong"` |
| `manual_lines` | `string` (6 chars) | conditional | `method=manual` 時輸入 6 個數字（6/7/8/9）|
| `question` | `string` | optional | 問事描述 |
| `use_true_solar_time` | `boolean` | optional | 預設 `false` |
| `locale` | `string` | optional | `"zh-TW"` / `"zh-CN"` / `"en"` |

**範例**
```json
{
  "system": "ichingshifa",
  "method": "datetime",
  "datetime": "2026-08-04T14:30:00",
  "timezone": "Asia/Hong_Kong",
  "question": "事業轉職時機",
  "use_true_solar_time": false,
  "locale": "zh-TW"
}
```

**Response 200**
```json
{
  "system_id": "ichingshifa",
  "system_name": "周易筮法",
  "ganzhi": {
    "year": "庚午",
    "month": "辛巳",
    "day": "乙卯",
    "hour": "辛未"
  },
  "five_elements": ["木", "火", "土", "金", "水"],
  "main_judgment": "謙之升，動爻2根",
  "favorable": ["東南", "木火"],
  "unfavorable": ["西北"],
  "details": {
    "ben_gua": "謙",
    "zhi_gua": "升",
    "changed_lines": [2, 5]
  },
  "raw_output": "...",
  "computed_at": "2026-08-04T14:30:00Z"
}
```

**錯誤回應**（統一格式）
```json
{
  "error_code": "INVALID_DATETIME",
  "message": "Invalid datetime format. Use ISO 8601.",
  "details": { "received": "2026/08/04 14:30" }
}
```

---

## Error Codes

| Code | HTTP | 說明 |
|------|------|------|
| `INVALID_DATETIME` | 422 | 時間格式錯誤 |
| `INVALID_TIMEZONE` | 422 | 時區無效 |
| `INVALID_MANUAL_LINES` | 422 | 手動爻值格式錯誤 |
| `UNSUPPORTED_SYSTEM` | 422 | 不支援的術數（Phase 1 僅有 ichingshifa）|
| `MISSING_LOCATION` | 422 | 占星系統需要經緯度 |
| `SYSTEM_COMPUTATION_FAILED` | 500 | 術數計算失敗 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超過呼叫頻率限制 |

---

## 後續端點（規劃中）

- `POST /api/interpret` — AI 綜合解讀
- `GET /api/systems` — 列出可用術數與輸入需求（已實作）

---

### `POST /api/compare`

**多系統並排比較**。單一請求跑多個術數，回傳結果陣列 + 跨系統分析。

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `systems` | `string[]` | optional | 要跑的系統 ID 清單；省略時跑全部已註冊模組 |
| `method` | `string` | ✅ | `random` / `datetime` / `manual` |
| `datetime` | `string` (ISO 8601) | conditional | method=datetime 時必填 |
| `timezone` | `string` | optional | IANA 時區 |
| `manual_lines` | `string` | conditional | method=manual（限 ichingshifa）|
| `question` | `string` | optional | 問事描述 |
| `latitude` / `longitude` | `float` | optional | 經緯度（占星必填）|
| `use_true_solar_time` | `bool` | optional | 預設 `false` |
| `per_system` | `object` | optional | 每系統的專屬 knob，如 `{"qimen":{"variant":"zhirun"}, "taiyi":{"scope":"nianji"}}` |

**範例請求**
```json
{
  "datetime": "2026-08-04T14:30:00",
  "question": "事業轉職時機",
  "per_system": {
    "qimen": { "variant": "zhirun" },
    "taiyi": { "scope": "nianji", "formula": "jinjing" }
  }
}
```

**Response 200**
```json
{
  "results": [ /* DivinationResult[], 每個系統一份 */ ],
  "cross_analysis": {
    "consensus": "neutral",
    "verdict_counts": { "inauspicious": 2, "neutral": 2 },
    "timings": ["unknown", "ongoing", "early", "early"],
    "entities_by_system": {
      "周易筮法": ["本卦：離", "之卦：旅"],
      "大六壬":   ["初傳：巳", "中傳：申", "末傳：寅", "格局：伏吟", "格局：自任"],
      "奇門遁甲": ["天乙：芮", "星宮：心(坤)", "門宮：開(乾)"],
      "太乙神數": ["太乙：坤", "紀元：第四紀庚子元", ...]
    },
    "overlap": [
      "系統間存在分歧",
      "時機：不同系統給出不同時間窗"
    ],
    "differences": [
      "周易筮法：inauspicious",
      "大六壬：inauspicious",
      "奇門遁甲：neutral",
      "太乙神數：neutral"
    ]
  },
  "failures": [],
  "question": "事業轉職時機",
  "computed_at": "2026-08-04T..."
}
```

**錯誤回應**（單一系統失敗不會中斷整體請求）
- 422：method 與 systems 不相容（例如 method=random + systems=[liuren]）

---

## 支援的術數 (Phase 2)

### ichingshifa（周易筮法）

| 項目 | 說明 |
|------|------|
| **System ID** | `ichingshifa` |
| **System Name** | 周易筮法 |
| **支援 method** | `random`, `datetime`, `manual` |
| **必填欄位** | method=datetime → `datetime` + `timezone`；method=manual → `manual_lines`（6 位數字 6/7/8/9）|
| **回傳 details** | `ben_gua_name`, `zhi_gua_name`, `changed_lines` 等 |
| **底層函式庫** | [kentang2017/ichingshifa](https://github.com/kentang2017/ichingshifa) |

### liuren（大六壬）

| 項目 | 說明 |
|------|------|
| **System ID** | `liuren` |
| **System Name** | 大六壬 |
| **支援 method** | 僅 `datetime`（隨機起課不適用於傳統大六壬）|
| **必填欄位** | `datetime`（後端自動推算節氣、農曆月、日時干支）|
| **回傳 details** | `san_chuan`（三傳）、`si_ke`（四課）、`tian_di_pan`（天地盤）、`shen_sha`（神煞）、`ge_ju`（格局）、`ri_ma`（日馬）|
| **底層函式庫** | [kentang2017/kinliuren](https://github.com/kentang2017/kinliuren) |

**範例請求**
```json
{
  "system": "liuren",
  "method": "datetime",
  "datetime": "2026-05-15T14:30:00",
  "timezone": "Asia/Hong_Kong"
}
```

### qimen（奇門遁甲）

| 項目 | 說明 |
|------|------|
| **System ID** | `qimen` |
| **System Name** | 奇門遁甲 |
| **支援 method** | 僅 `datetime` |
| **必填欄位** | `datetime`（後端自動推算） |
| **選填變體** | `details.variant`: `chabu` (時家拆補, 預設), `zhirun` (時家置閏), `ke_chabu` (刻家拆補), `ke_zhirun` (刻家置閏), `jinhanyujing` (金函玉鏡日家) |
| **回傳 details** | `排盤方式`, `排局`, `節氣`, `值符值使`, `天盤`, `地盤`, `門`, `星`, `神`, `馬星`, `長生運` |
| **底層函式庫** | [kentang2017/kinqimen](https://github.com/kentang2017/kinqimen) |
| **特殊處理** | Upstream 套件 `__init__.py` 為空，使用 `importlib.util` 直載 `kinqimen.py` |

**範例請求（金函玉鏡日家奇門）**
```json
{
  "system": "qimen",
  "method": "datetime",
  "datetime": "2026-08-04T14:30:00",
  "details": { "variant": "jinhanyujing" }
}
```

### taiyi（太乙神數）

| 項目 | 說明 |
|------|------|
| **System ID** | `taiyi` |
| **System Name** | 太乙神數 |
| **支援 method** | 僅 `datetime` |
| **必填欄位** | `datetime` |
| **選填 scope** | `details.scope`: `fenji` (分計, 預設), `nianji` (年計), `yueji` (月計), `riji` (日計), `shiji` (時計) |
| **選填 formula** | `details.formula`: `tongzong` (太乙統宗, 預設), `jinjing` (太乙金鏡), `taojinge` (太乙淘金歌), `ju` (太乙局) |
| **回傳 details** | `太乙計`, `太乙公式類別`, `紀元`, `太歲`, `局式`, `太乙落宮`, `太乙`, `天乙`, `地乙`, `主算`, `客算`, `定算` 等 |
| **底層函式庫** | [kentang2017/kintaiyi](https://github.com/kentang2017/kintaiyi) |
| **特殊處理** | 同樣 bypass `__init__.py`；numpy 標量遞迴轉原生型別 |

**範例請求（年計 · 太乙金鏡）**
```json
{
  "system": "taiyi",
  "method": "datetime",
  "datetime": "2026-08-04T14:30:00",
  "details": { "scope": "nianji", "formula": "jinjing" }
}
```