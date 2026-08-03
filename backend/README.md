# Backend · shushu-hub

FastAPI 後端，提供多術數統一排盤 API。

## 快速啟動

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # 視需要調整
uvicorn app.main:app --reload --port 8000
```

## 互動式 API 文件

啟動後造訪：

- Swagger UI：<http://localhost:8000/docs>
- ReDoc：<http://localhost:8000/redoc>

## 測試

```bash
pytest -v
```

## Docker

```bash
docker build -t shushu-hub-backend .
docker run -p 8000:8000 shushu-hub-backend
```

## 目錄結構

```
app/
├── main.py              # FastAPI app
├── config.py            # 設定
├── api/                 # REST endpoints
├── core/                # 共用工具 (ganzhi, lunar, ...)
├── modules/             # 術數 adapters
├── ai/                  # AI 整合 (mock)
└── schemas/             # Pydantic models
```

## 環境變數

參考 `.env.example`。所有變數都有合理預設值。