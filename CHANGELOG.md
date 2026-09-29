# Changelog

本檔記錄每次 release。格式：版本、日期、更新內容、Git commit short SHA。

## [v1.1.0] - 2026-09-29
Commit: _（待 deploy 後補）_

### 新增
- **CMS 後台新增廣告影片上傳／管理**：管理員可喺 admin 頁「廣告管理」tab 直接上傳 mp4 廣告片（multipart 上傳，存落 `/static/ads/<uuid8>.mp4`）、睇預覽、即時切換啟用／停用、同埋刪除（連影片檔一併清走）。只收 `.mp4` / `video/mp4`，其他格式 400 拒收。
- 後端新 model `Ad`（id / title / video_url / duration 預設 20 秒 / active 預設啟用 / created_at），migration `c7d8e9f0a1b2` 建 `ads` 表；新 CMS 端點 `POST /cms/ads/upload`、`GET /cms/ads`、`PUT /cms/ads/{id}`、`DELETE /cms/ads/{id}`（全部沿用 `require_admin`）。
- 後端依賴加 `python-multipart`（FastAPI 檔案上傳所需）。

## [v1.0.1] - 2026-09-29
Commit: _（待 deploy 後補）_

### 修復
- **播放頁「下一集／上一集」按鈕撳唔到／冇反應**：
  1. 之前 `goPrev`/`goNext` 用 `router.push('/play/?episode=X')`，但 Next.js App Router 唔會重新 mount 同一個 `/play` 頁 component，`useEffect([])` 唔會再跑，`episodeId` state 維持舊值，依賴 `[episodeId]` 嘅 `loadEpisode()` 唔會觸發——URL 變咗但影片仲係舊集。改成切集直接 `setEpisodeId(targetId)`，由既有 `useEffect([episodeId])` 自動切片；URL 用 `window.history.replaceState` 同步（用 `location.pathname` 自動配合 production basePath `/short-drama-platform/`），refresh／share 都落返正確集數，唔會 reload。
  2. 後端 `/episodes/{id}` 從來冇回傳 `prev_episode_id`／`next_episode_id`（前端 interface 一早 define 咗但後端冇填），導致上下集掣長期 disabled。前端開播時額外拉一次 `/dramas/{drama_id}`，喺成個劇集嘅集數 list 入面自己搵上／下一集 id，並順便填返頂 bar 嘅劇名。

### 其他
- 播放頁切集時一併 reset `videoError`／`comingSoon`／`loading`（`loadEpisode()` 入面已有）。

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
