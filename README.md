# 短劇平台（Short Drama Platform）

一個短劇影音平台的 monorepo，包含 FastAPI 後端與 Next.js + TypeScript Web 前端。

> iOS / Android 客戶端暫緩開發，本次以 Web 為唯一前端。

## 功能總覽

- 🔐 **電話 OTP 登入**：6 位數驗證碼、60 秒冷卻、每號碼每日 5 次上限（開發期 mock，驗證碼印在 server log）
- 📚 **劇集管理**：分類、劇集、集數 CRUD，支援篩選、搜尋、分頁
- ▶️ **播放模組**：影片串流位址、觀看進度自動上報
- 🛠️ **最小 CMS**：後台上架劇集與集數
- 🌐 **Web 前端**：Next.js 靜態匯出，可部署 GitHub Pages

## 目錄結構

```
.
├── backend/              # Python FastAPI 後端
│   ├── app/
│   │   ├── api/          # 路由：auth / dramas / episodes / categories / cms
│   │   ├── core/         # JWT 安全、依賴注入
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 請求/回應模型
│   │   └── services/     # OTP 邏輯、Redis 客戶端
│   ├── alembic/          # 資料庫遷移
│   ├── tests/            # pytest（SQLite 記憶體 + fakeredis，不需外部服務）
│   ├── .env.example
│   └── requirements.txt
├── web/                  # Next.js + TypeScript 前端
│   ├── app/              # App Router 頁面（首頁 / 登入 / 劇集詳情 / 播放）
│   ├── components/       # 共用元件
│   ├── lib/              # API 客戶端、auth 工具
│   ├── types/            # TypeScript 型別
│   ├── .env.example
│   └── next.config.js    # output: 'export' 靜態匯出
├── .github/workflows/
│   ├── ci.yml            # 後端 pytest CI
│   └── pages.yml         # Web 部署到 GitHub Pages
├── docker-compose.yml    # PostgreSQL 16 + Redis 7
└── .gitignore
```

## 快速啟動

### 1. 啟動基礎設施（PostgreSQL + Redis）

```bash
docker compose up -d
```

- PostgreSQL：`localhost:5432`（使用者 `postgres`、密碼 `postgres`、資料庫 `drama`）
- Redis：`localhost:6379`

### 2. 啟動後端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

後端啟動後：
- API 文件（Swagger）：http://127.0.0.1:8000/docs
- 健康檢查：http://127.0.0.1:8000/health

**Mock OTP 登入流程**（開發期，驗證碼不傳簡訊，印在 server log）：

```bash
# 1. 發送驗證碼（查看後端 terminal 輸出的 OTP）
curl -X POST http://127.0.0.1:8000/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+85291234567"}'

# 2. 用 log 中的 6 位數驗證碼登入
curl -X POST http://127.0.0.1:8000/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+85291234567", "code": "123456"}'
# 回傳 access_token + refresh_token
```

### 3. 啟動前端

```bash
cd web
npm install
cp .env.example .env.local
npm run dev
```

前端開發伺服器：http://localhost:3000

> `.env.local` 中 `NEXT_PUBLIC_API_URL` 預設為 `http://127.0.0.1:8000`，指向本機後端。

### 4. 建置靜態網站（部署用）

```bash
cd web
npm run build
# 產出在 web/out/ 目錄，可部署到 GitHub Pages
```

## 開發期後端存取位址對照表

| 執行環境 | 後端位址 | 說明 |
|---|---|---|
| 本機開發（Web dev server） | `http://127.0.0.1:8000` | `NEXT_PUBLIC_API_URL` 預設值 |
| iOS 模擬器 | `http://127.0.0.1:8000` | 模擬器與主機共用 localhost |
| Android 模擬器 | `http://10.0.2.2:8000` | 模擬器特殊環回位址 |
| 實機（同一 LAN） | `http://<你的LAN IP>:8000` | 手機與電腦連同一 Wi-Fi |
| 外部測試 | ngrok 隧道位址 | `ngrok http 8000` 取得公開 URL |

## 測試

### 後端

```bash
cd backend
pytest -v
```

測試使用 SQLite 記憶體資料庫 + fakeredis，**不需啟動 PostgreSQL/Redis**。

### CI

`.github/workflows/ci.yml` 在 push / PR 時自動於 ubuntu-latest 上起 postgres + redis services 跑 pytest。

## 部署

### Web → GitHub Pages

`.github/workflows/pages.yml` 會在 push 到 `main` 時自動：
1. `npm ci && npm run build`（靜態匯出）
2. 部署 `web/out/` 到 GitHub Pages

需在 repo **Settings → Pages → Build and deployment → Source** 選擇 **GitHub Actions**。

部署後網址：`https://<你的username>.github.io/short-drama-platform/`

> 注意：GitHub Pages 上的靜態網站呼叫後端 API 時，`NEXT_PUBLIC_API_URL` 需指向一個公開可達的後端位址（開發期可用 ngrok）。

## 技術棧

| 層面 | 技術 |
|---|---|
| 後端 | Python 3.11+、FastAPI、SQLAlchemy 2.x、Pydantic v2、Alembic |
| 資料庫 | PostgreSQL 16 |
| 快取/OTP | Redis 7 |
| 認證 | JWT（access 15 分鐘 + refresh 7 天） |
| 前端 | Next.js 14（App Router）、TypeScript（strict）、CSS Modules |
| 部署 | GitHub Pages（靜態匯出）、GitHub Actions CI/CD |
| 容器 | Docker Compose（本機開發用） |

## 後端 API 一覽

### 認證
| 方法 | 路徑 | 說明 | 認證 |
|---|---|---|---|
| POST | `/auth/otp/request` | 發送 OTP 驗證碼 | ❌ |
| POST | `/auth/otp/verify` | 驗證 OTP 並取得 token | ❌ |
| POST | `/auth/refresh` | 刷新 access token | ❌ |
| GET | `/auth/me` | 取得當前使用者 | ✅ |

### 公開讀取
| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/categories` | 分類列表 |
| GET | `/dramas` | 劇集列表（支援 category、search、page、page_size） |
| GET | `/dramas/{id}` | 劇集詳情（含集數列表） |
| GET | `/episodes/{id}` | 集數詳情 |

### 播放（需登入）
| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/episodes/{id}/stream` | 取得播放位址 |
| POST | `/episodes/{id}/progress` | 上報觀看進度 |
| GET | `/dramas/{id}/progress` | 取得劇集觀看進度 |

### CMS（需登入）
| 方法 | 路徑 | 說明 |
|---|---|---|
| POST/PUT/DELETE | `/cms/categories` | 分類管理 |
| POST/PUT/DELETE | `/cms/dramas` | 劇集管理 |
| POST/PUT/DELETE | `/cms/episodes` | 集數管理 |

## 未來規劃

- [ ] iOS / Android 客戶端（React Native 或原生）
- [ ] 真實 SMS 閘道整合（Twilio / 阿里云）
- [ ] 影片轉碼與 CDN
- [ ] 使用者角色與權限（admin / viewer）
- [ ] 付費與解鎖機制
- [ ] 推播通知
