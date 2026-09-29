# Changelog

本檔記錄每次 release。格式：版本、日期、更新內容、Git commit short SHA。

## [v1.0.0] - 2026-09-29
Commit: c8d9155

### 修復
- **影片播放（根治）**：紅果 CDN 簽名 URL 約 1 小時過期、外站 Referer 會被防盗鏈 403。改為開播時即時由紅果 player 頁重簽新 URL，並經後端 `/episodes/{id}/media?token=` 代理串流（Range/206），前端永遠唔會再見到過期黑畫面。
- **登入記憶**：bootstrap session 全 App 只跑一次、完成後 broadcast `auth-changed` 更新 Navbar；ProtectedRoute 等 bootstrap 完成先決定跳轉；refresh 時唔再寫入 `user=null` 蓋掉本機使用者。
- 後端單元測試 `test_stream_requires_login` 對齊新媒體代理契約（CI 轉綠）。

### 新增
- 劇集卡片同詳情頁顯示「來自：紅果短劇」來源 badge。
- 版本號：Web footer 顯示 `v1.0.0`（`NEXT_PUBLIC_APP_VERSION` 由 package.json 注入）；Android `versionCode=1` / `versionName=1.0.0`，App 選單「關於」彈窗顯示版本。
- 後端 QA 腳本 `backend/scripts/qa_check.py`（一鍵檢查後端/tunnel/登入/播放）。
- 本 Changelog 同 `QA_CHECKLIST.md`、`RETROSPECTIVE.md`。

### 已知
- 紅果只開放頭幾集公開；其餘集要登入/App 先解鎖，未開放集顯示「敬請期待」，唔係壞。
- cloudflared 免費 tunnel URL 重啟後會變，要同步更新 `.github/workflows/pages.yml` 嘅 `NEXT_PUBLIC_API_URL` 再部署。
