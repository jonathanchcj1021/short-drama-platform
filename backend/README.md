# 短劇平台後端（FastAPI）

短劇平台 monorepo 的後端服務，提供電話 OTP 登入、劇集/集數/分類管理、播放與觀看進度、最小 CMS。

## 技術棧

- Python 3.11+ / FastAPI / SQLAlchemy 2.x（sync）/ Pydantic v2
- PostgreSQL 16、Redis 7（本機以 docker-compose 起，由 monorepo 根目錄統一處理）
- JWT（access 15 分鐘 + refresh 7 天）
- Alembic 遷移、pytest（以記憶體 SQLite + fakeredis 跑測試，不需外部服務）

## 快速開始

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # 依本機環境調整 DATABASE_URL / REDIS_URL / JWT_SECRET
```

### 初始化資料庫

```bash
alembic upgrade head
```

### 啟動服務

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- 健康檢查：`GET http://localhost:8000/health` → `{"status":"ok"}`
- API 文件：`http://localhost:8000/docs`

## 測試

```bash
pytest
```

測試使用記憶體 SQLite 與 fakeredis，不需啟動 PostgreSQL / Redis。

## 主要流程

### OTP 登入（開發期不接真實 SMS）

1. `POST /auth/otp/request` body `{"phone_number": "+8869..."}`
   - 產生 6 位驗證碼存 Redis（TTL 5 分鐘）
   - 同號碼 60 秒內不可重發（回 429）；每號碼每日上限 5 次
   - **驗證碼會印在 server log**：`OTP for +8869...: 123456`
2. `POST /auth/otp/verify` body `{"phone_number": "...", "code": "123456"}`
   - 回傳 access_token / refresh_token / user
3. `POST /auth/refresh` body `{"refresh_token": "..."}` 換新 access token
4. `GET /auth/me`（Bearer access token）

### 劇集

- 公開讀取：`GET /dramas`（支援 `category_id`、`search`、`skip`、`limit`）、`GET /dramas/{id}`（含 episodes）、`GET /categories`、`GET /episodes/{id}`
- 需登入：`GET /episodes/{id}/stream`、`POST /episodes/{id}/progress`、`GET /dramas/{id}/progress`
- CMS 寫入（`/cms/...`）需登入，目前不區分角色，有 token 即可

## 目錄結構

```
backend/
├── app/            # FastAPI 應用
├── alembic/        # 資料庫遷移
├── tests/          # pytest
├── .env.example
├── requirements.txt
└── alembic.ini
```
