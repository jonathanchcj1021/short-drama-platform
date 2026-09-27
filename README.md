# 短劇平台（Short Drama Platform）

一個短劇影音平台的 monorepo，包含 FastAPI 後端、Next.js + TypeScript Web 前端，以及 Kotlin + Jetpack Compose Android 客戶端。

> iOS 客戶端暫不開發。本次涵蓋後端、Web 與 Android。

## 功能總覽

- 🔐 **電話 OTP 登入**：6 位數驗證碼、60 秒冷卻、每號碼每日 5 次上限（開發期 mock，驗證碼印在 server log）
- 📚 **劇集管理**：分類、劇集、集數 CRUD，支援篩選、搜尋、分頁
- ▶️ **播放模組**：影片串流位址、觀看進度自動上報
- 🛠️ **最小 CMS**：後台上架劇集與集數
- 🌐 **Web 前端**：Next.js 靜態匯出，可部署 GitHub Pages
- 📱 **Android 客戶端**：Kotlin + Jetpack Compose + Media3 ExoPlayer，登入／首頁／詳情／播放 MVP

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
│   ├── Dockerfile        # 生產映像（multi-stage）
│   ├── .env.example
│   └── requirements.txt
├── web/                  # Next.js + TypeScript 前端
│   ├── app/              # App Router 頁面（首頁 / 登入 / 劇集詳情 / 播放）
│   ├── components/       # 共用元件
│   ├── lib/              # API 客戶端、auth 工具
│   ├── types/            # TypeScript 型別
│   ├── .env.example
│   └── next.config.js    # output: 'export' 靜態匯出
├── android/              # Kotlin + Jetpack Compose Android 客戶端
│   ├── app/src/main/java/com/drama/app/
│   │   ├── data/         # API、model、repository
│   │   ├── ui/           # 登入／首頁／詳情／播放頁
│   │   ├── navigation/   # NavHost
│   │   └── di/           # 手動 DI 容器
│   ├── app/build.gradle.kts
│   └── README.md         # Android Studio 開發說明
├── .github/workflows/
│   ├── ci.yml            # 後端 pytest CI
│   ├── android-ci.yml    # Android Gradle build CI
│   └── pages.yml         # Web 部署到 GitHub Pages
├── docker-compose.yml    # PostgreSQL 16 + Redis 7（本機開發）
├── render.yaml           # Render Blueprint（後端 + PostgreSQL 免費層部署）
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

### 5. Android App（本機 Emulator 開發）

#### 先決條件
- Android Studio Hedgehog（2023.1.1）或更新版本
- JDK 17（Android Studio 內建即可）
- Android SDK 34
- 至少 8GB RAM（Emulator 比較吃資源）

#### 步驟

1. **用 Android Studio 開啟專案**
   - 開 Android Studio → `File` → `Open` → 選擇 `android/` 目錄
   - 等待 Gradle Sync 完成（第一次會下載依賴，需幾分鐘）

2. **建立 Android Emulator**
   - 右上角 `Device Manager` → `Create Device`
   - 選擇 `Pixel 6`（或任何手機）→ `Next`
   - 選擇系統映像 `API 34`（Android 14）→ `Next` → `Finish`
   - 點擊 ▶ 啟動 Emulator

3. **啟動後端（本機）**
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   > `--host 0.0.0.0` 很重要：Emulator 唔係用 `127.0.0.1` 連主機，而係用 `10.0.2.2`。

4. **App 連接後端**
   - 預設 `BuildConfig.API_BASE_URL = http://10.0.2.2:8000`（Emulator 內 `10.0.2.2` = 主機 `127.0.0.1`）
   - 如需改位址：在 `android/local.properties` 加 `api.base.url=http://你的IP:8000`

5. **安裝並執行 App**
   - Android Studio 頂部選 Emulator，點擊 ▶ Run（或 `^R`）
   - App 安裝到 Emulator 並自動開啟

#### 命令列建置（不需 Android Studio）

專案已包含 Gradle Wrapper，直接用 `./gradlew` 即可：

```bash
cd android

# 首次：設定 SDK 路徑（Android Studio 開過一次會自動寫入）
echo "sdk.dir=$HOME/Library/Android/sdk" > local.properties

# 建置 Debug APK
./gradlew assembleDebug
# → app/build/outputs/apk/debug/app-debug.apk

# 安裝到已啟動嘅 Emulator / 連接嘅實機
./gradlew installDebug
```

> 需要 JDK 17 + Android SDK。詳細 macOS 設定、疑難排解見 `android/README.md` 第 10 節。

#### Mock OTP 登入流程
1. App 登入頁輸入電話號碼 → 點「發送驗證碼」
2. **睇後端 terminal log**，會印出 `OTP for +852...: 123456`
3. 將 6 位數輸入 App → 點「驗證登入」
4. 成功後跳轉首頁

#### 已知限制
- 開發期 `AndroidManifest` 開了 `usesCleartextTraffic="true"`（連本機 http 後端需要），生產前需改用 HTTPS
- 影片用靜態 mp4 佔位，未接轉碼/CDN

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

**需要使用者手動做一次：**
1. 到 repo **Settings → Pages → Build and deployment → Source**
2. 選擇 **GitHub Actions**
3. 之後每次 push 到 `main` 就會自動部署

部署後網址：`https://<你的username>.github.io/short-drama-platform/`

> 注意：GitHub Pages 上的靜態網站呼叫後端 API 時，`NEXT_PUBLIC_API_URL` 需指向一個公開可達的後端位址（即下面 Render 部署後的 URL）。

### Backend → Render 免費層

`render.yaml`（Blueprint）已定義好後端 Web Service + PostgreSQL，一鍵部署。

**需要使用者做嘅步驟：**

1. **註冊 Render 帳號**（免費）：https://dashboard.render.com/register ，用 GitHub 登入
2. **建立 Upstash Redis**（免費層，Render 免費層唔包 Redis）：
   - 到 https://upstash.com 註冊 → 建立 Redis database
   - 複製 `REST URL` 或 `Redis URL`（`redis://...` 格式）
3. **Render 部署：**
   - Render Dashboard → `New` → `Blueprint`
   - 連接你嘅 GitHub repo（`short-drama-platform`）
   - Render 會自動讀取 `render.yaml`
   - 喺 Environment Variables 填入 `REDIS_URL`（步驟 2 嘅 Upstash URL）
   - `JWT_SECRET` 會由 Render 自動產生
   - 點 `Apply` 開始部署
4. **部署完成後**，Render 會俾一個 URL（例如 `https://short-drama-backend.onrender.com`）
5. **更新 Web 嘅 API 位址**：修改 `web/.env.example` 或喺 GitHub Pages workflow 設定 `NEXT_PUBLIC_API_URL` 指向 Render URL

#### 後端生產環境變數

| 變數 | 說明 | render.yaml 處理 |
|---|---|---|
| `DATABASE_URL` | PostgreSQL 連線字串 | ✅ 自動從 Render DB 注入 |
| `REDIS_URL` | Redis 連線字串（Upstash） | ⚠️ 需手動填入 |
| `JWT_SECRET` | JWT 簽名密鑰 | ✅ Render 自動產生 |
| `JWT_ALGORITHM` | 預設 HS256 | ✅ 已設 |
| `PORT` | 監聽端口 | ✅ Render 自動注入 |

#### 生產 Dockerfile

`backend/Dockerfile` 用 multi-stage build：
- Builder：安裝 gcc + libpq-dev 編譯 psycopg2
- Runtime：python:3.11-slim，只含執行期依賴
- 啟動時自動跑 `alembic upgrade head` 再起 uvicorn
- 非 root user 執行

> Render 免費層 Web Service 會喺 15 分鐘無流量後休眠，首次呼叫需 30-50 秒醒機。PostgreSQL 免費層有效期 90 日。

## 技術棧

| 層面 | 技術 |
|---|---|
| 後端 | Python 3.11+、FastAPI、SQLAlchemy 2.x、Pydantic v2、Alembic |
| 資料庫 | PostgreSQL 16 |
| 快取/OTP | Redis 7（本機）／Upstash（生產） |
| 認證 | JWT（access 15 分鐘 + refresh 7 天） |
| Web 前端 | Next.js 14（App Router）、TypeScript（strict）、CSS Modules |
| Android 客戶端 | Kotlin、Jetpack Compose（Material 3）、Media3 ExoPlayer、Retrofit |
| 部署 | GitHub Pages（Web）、Render 免費層（Backend）、GitHub Actions CI/CD |
| 容器 | Docker Compose（本機開發）、Dockerfile（生產） |

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

- [ ] iOS 客戶端（暫不開發）
- [ ] 真實 SMS 閘道整合（Twilio / 阿里云）
- [ ] 影片轉碼與 CDN
- [ ] 使用者角色與權限（admin / viewer）
- [ ] 付費與解鎖機制
- [ ] 推播通知
