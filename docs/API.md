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
| `system` | `string` | ✅ | `"ichingshifa"` (Phase 1) |
| `method` | `string` | ✅ | `"random"` / `"datetime"` / `"manual"` |
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

- `POST /api/compare` — 多系統並排比較
- `POST /api/interpret` — AI 綜合解讀
- `GET /api/systems` — 列出可用術數與輸入需求