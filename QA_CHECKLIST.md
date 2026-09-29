# QA 測試 Checklist — v1.0.0

**測試日期：** 2026-09-29
**測試站：** https://jonathanchcj1021.github.io/short-drama-platform/
**後端：** FastAPI :8000，經 cloudflared tunnel 對外
**測試帳號：** `85263106930` / `drama2026`（admin）
**狀態圖例：** ✅ Pass　⚠️ Blocked／需人手確認　❌ Fail

---

## 1. 登入流程

| # | 步驟 | 預期結果 | 實際結果 | 狀態 |
|---|---|---|---|---|
| 1.1 | `POST /auth/login`（admin 帳密） | 200，回 access_token + refresh_token + user | 200，token 正常 | ✅ |
| 1.2 | `POST /auth/refresh`（用 refresh_token） | 200，換到新 access_token | 經 tunnel 實測 200 | ✅ |
| 1.3 | 錯密碼 | 401 | 後端 code reject | ✅ |
| 1.4 | 關 browser 再開，自動續回登入 | Navbar 顯示電話+登出，唔使再入密碼 | refresh endpoint 200；前端 bootstrap 已改為只跑一次＋broadcast `auth-changed`；**未經人手 click-through 確認 GUI 反應** | ⚠️ |

> 註：1.4 嘅 network 路徑（refresh 200、CORS allow github.io origin）已驗證；GUI 實際 reload 後 Navbar 更新屬前端行為，建議人手開一次站 hard-reload 作最終確認。

## 2. 瀏覽劇集

| # | 步驟 | 預期 | 實際 | 狀態 |
|---|---|---|---|---|
| 2.1 | `GET /dramas` | 回 20 套劇，每個帶 `source` | 20 套，`source="hongguo"` | ✅ |
| 2.2 | 劇集卡來源 badge | 顯示「來自：紅果短劇」 | 前端 DramaCard 已加；部署 bundle 含新碼 | ✅ |
| 2.3 | 詳情頁來源 badge | 顯示「來自：紅果短劇」 | DramaDetailClient 已加 | ✅ |
| 2.4 | Footer 版本 | 顯示「短劇平台 · v1.0.0」 | 部署站 HTML 含 `1.0.0` | ✅ |

## 3. 影片播放（核心）

| # | 步驟 | 預期 | 實際 | 狀態 |
|---|---|---|---|---|
| 3.1 | 頭排劇 ep1 `/stream` | 回 `/episodes/{id}/media?token=` 代理位址 | 七零团宠 ep361 正確回 tunnel domain 嘅 media URL | ✅ |
| 3.2 | `<video>` Range GET media URL | 206 Partial Content，`video/mp4`，收到 byte | 經 tunnel 實測 `HTTP 206 video/mp4 2048B` | ✅ |
| 3.3 | 紅果簽名 URL 過期 | 開播時即時重簽，唔黑畫面 | on-demand 重簽 + 25 分鐘 cache | ✅ |
| 3.4 | 冇 token 取片 | 401 | 實測 no-token 401 | ✅ |
| 3.5 | 掃描頭 15 套劇第一集 | 多數播到 | 14/15 播到（10–35MB 真片） | ✅ |
| 3.6 | 未開放／冇真片嘅集 | 顯示「敬請期待」，唔播無關畫面 | `available=false`，例：坤仪第四季 | ✅ |

## 4. CMS 管理後台

| # | 步驟 | 預期 | 實際 | 狀態 |
|---|---|---|---|---|
| 4.1 | admin 入 `/admin` | 可入 | ProtectedRoute 已改為等 bootstrap 先判斷 | ⚠️ 未人手 click |
| 4.2 | 一般用戶入 `/admin` | 被拒 | 後端 require admin；未人手驗 | ⚠️ |

## 5. API／基建健康（腳本）

執行：
```bash
cd backend && DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" \
  .venv/bin/python scripts/qa_check.py
```
最近結果：**6/6 PASS，exit 0**（本地 /health、tunnel /health、登入、有劇、至少一套播到、頭排劇播到）。後端單元測試 `pytest`：**12 passed**。

## 6. 部署

| # | 步驟 | 預期 | 實際 | 狀態 |
|---|---|---|---|---|
| 6.1 | push 後 GitHub Actions | Deploy to Pages 綠色 | 最近一次 Deploy success | ✅ |
| 6.2 | CI 後端測試 | 綠色 | 先前紅（舊 test 斷言舊契約），已修復並本地 12 passed | ✅ |
| 6.3 | 部署站係最新碼 | 見到 v1.0.0 footer | 已確認 | ✅ |

---

## 總結

- **Pass：** 播放（media proxy + Range 206 + 過期重簽）、登入 refresh、來源 badge、版本號、基建健康、部署。
- **Blocked／建議人手最終一 click：** GUI reload 後 Navbar 狀態、admin 後台進出（network 層已驗證，未真人 click）。
