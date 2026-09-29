# 短劇聚合平台 — 項目總覽

## 🎯 目的
一個低成本短劇聚合平台：爬紅果短劇熱播榜 → 展示劇集列表 → 播放器睇片。含用戶登入、CMS 管理、播放記錄。

---

## 🏗️ 架構

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Web (Next) │     │  Android    │     │  iOS (唔做)  │
│  GitHub Pages│     │  Kotlin     │     │             │
└──────┬──────┘     └──────┬──────┘     └─────────────┘
       │                   │
       └───────┬───────────┘
               ▼
     ┌─────────────────┐
     │  FastAPI (Python)│  ← cloudflared tunnel
     │  Port 8000       │
     └────────┬────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌─────────┐      ┌─────────┐
│Postgres │      │ Redis   │
│Docker   │      │Docker   │
│:5433    │      │:6379    │
└─────────┘      └─────────┘
```

---

## 📁 Code Paths

| 層 | 路徑 | 技術 |
|---|---|---|
| **Backend** | `~/short-drama-platform/backend/` | FastAPI + SQLAlchemy + Alembic |
| **Web** | `~/short-drama-platform/web/` | Next.js 14 (static export) + TypeScript |
| **Android** | `~/short-drama-platform/android/` | Kotlin + MVVM + Retrofit |
| **DB** | Docker `drama-db` | Postgres on :5433 |
| **Cache** | Docker `drama-redis` | Redis on :6379 |
| **Tunnel** | cloudflared quick tunnel | → `localhost:8000` |
| **Deploy** | GitHub Pages | `jonathanchcj1021.github.io/short-drama-platform/` |

---

## 🔑 Backend 檔案

| 路徑 | 用途 |
|---|---|
| `app/main.py` | FastAPI entry，mount `/static` |
| `app/api/auth.py` | 登入/註冊/refresh/me |
| `app/api/cms.py` | 管理後台 CRUD（admin only） |
| `app/api/dramas.py` | 劇集列表/詳情 |
| `app/api/episodes.py` | 集數 + 播放 stream |
| `app/api/categories.py` | 分類 |
| `app/api/google_auth.py` | Google SSO（未完成） |
| `app/models/` | User / Drama / Episode / Category / WatchProgress |
| `scripts/crawler/` | 每日爬紅果短劇熱播榜 |
| `alembic/versions/` | DB migration |

---

## 🌐 Web 檔案

| 路徑 | 用途 |
|---|---|
| `app/page.tsx` | 首頁（劇集 grid） |
| `app/drama/page.tsx` | 劇集詳情 + 集數列表 |
| `app/play/PlayClient.tsx` | 播放器 |
| `app/login/page.tsx` | 登入/註冊 |
| `app/admin/page.tsx` | CMS 後台 |
| `lib/apiClient.ts` | fetch 包裝 + auto refresh token |
| `lib/auth.ts` | localStorage token 管理 |

---

## 📱 Android 檔案

| 路徑 | 用途 |
|---|---|
| `MainActivity.kt` | 入口 |
| `ui/home/HomeScreen.kt` | 首頁 |
| `ui/detail/DramaDetailScreen.kt` | 劇集詳情 |
| `ui/play/PlayScreen.kt` | 播放器 |
| `ui/login/LoginScreen.kt` | 登入 |
| `data/api/ApiService.kt` | Retrofit API |
| `util/TokenManager.kt` | token 存儲 |

---

## ⚙️ 運行命令

```bash
# Backend
cd ~/short-drama-platform/backend
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" \
  .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

# Crawler
DATABASE_URL="..." .venv/bin/python -m scripts.crawler.crawl --limit 30

# Web dev
cd web && npm run dev

# Tunnel
cloudflared tunnel --url http://127.0.0.1:8000
```
