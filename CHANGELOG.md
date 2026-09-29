# Changelog

本檔記錄每次 release。格式：版本、日期、更新內容、Git commit short SHA。

## [v1.2.0] - 2026-09-29
Commit: _（待 deploy 後補）_

### 新增 — 多來源短劇爬蟲（唔再淨係紅果）
- **優酷短劇（youku）**：新增公開搜尋結果頁爬蟲 `backend/scripts/crawler/youku.py`，由 `so.youku.com` 短劇關鍵字 SSR 頁（`window.__INITIAL_DATA__` JSON）抽劇名／封面／集數／獨播 VIP 角標／年份／簡介。**只匯入 metadata**：優酷正片全 DRM/VIP，攞唔到公開片 URL，集數留空，唔造假。實際匯入 **40 部優酷短劇**。
- **爬蟲 CLI 支援多來源**：`crawl.py` 改做 source registry（`CRAWLERS` dict），`--source` 接受 `hongguo / youku / fanqie / douyin / all`；`all` 順序跑晒已註冊來源，單一來源失敗唔會成條鏈斷。`source` 欄位如實標記每部劇來源；`hongguo_series_id` 只紅果先填（其他來源留空）。
- **誠實 placeholder adapter**：`fanqie.py`（番茄短劇）、`douyin.py`（抖音短劇）。實探確認暫時冇公開網頁片單，adapter 會真係抓一次首頁確認現況後回傳空 list，將來官方一開放網頁頻道就落 parser。
- 前端來源 badge 映射 `web/lib/sources.ts` 加 youku／fanqie／douyin 顯示名。

### 已知 — 市面主要短劇 app 公開網頁實探結論（唔造假）
- **可抓**：紅果（已有，32 部／363 集公開可播）、優酷（新，40 部 metadata-only）。
- **app-only / 反爬牆，冇接 adapter**：番茄短劇（fanqienovel.com 係小說站，短劇只係 App 入面 tab；官方網頁短劇入口其實就係紅果）、抖音短劇（douyin.com 係 SPA＋`a_bogus` 簽名牆，分享頁有 secsdk captcha）、快手星芒（robots 全站禁＋連線 timeout，消費片單只喺 App／小程序）、騰訊微視／騰訊視頻短劇（頻道跳錯誤頁、cover 頁靠簽名 API＋DRM fMP4）、愛奇藝／芒果 TV（server-side 全係 SPA/Nuxt 空殼）、九州／麥芽／點眾（企業營銷落地頁，冇公開片單）。完整探測記錄見 `backend/scripts/crawler/NEW_SOURCES_PROBE.md`。


## [v1.1.0] - 2026-09-29
Commit: _（待 deploy 後補）_

### 新增 — 免費 / VIP 會員制（Freemium）
- **會員等級**：`users` 加 `membership_tier`（`free` / `vip_monthly` / `vip_yearly`，預設 `free`）同 `vip_expires_at`；migration `b1c2d3e4f5a6`。有效 VIP = tier 非 free 且 `vip_expires_at` 未過期。
- **免費用戶限制**：每套收費劇頭 10 集免費任睇；第 11 集起播放前要睇 20 秒廣告倒數先解鎖（前端假廣告 creative 輪播，唔接廣告聯盟）。每集只需睇一次——`episode_unlocks` 表記錄已解鎖集數，重入直接播。
- **VIP 訂閱（模擬付款）**：`POST /billing/subscribe?plan=monthly|yearly` 即時 set 到期日（月 30 日 / 年 365 日，續訂由現有到期日延長）；`GET /billing/me` 查狀態連價錢。月費 HK$28、年費 HK$288。
- **播放閘（後端強制）**：`GET /episodes/{id}/stream` 對免費用戶第 11 集起回 `requires_ad=true`（無 video_url）；媒體代理 `/episodes/{id}/media` 未解鎖直連 403，防止繞過。VIP 同收費劇以外直接放行。
- **新「升級 VIP」頁** `/upgrade`：月費／年費 plan card、模擬訂閱、訂閱後即時顯示到期日。
- **Navbar**：免費用戶「免費會員」badge + 金色「升級 VIP」；VIP 顯示「VIP · 到期 YYYY-MM-DD」金底 badge。
- **劇集詳情**：收費劇第 11 集起顯示 🔒；`dramas.is_paid`（預設 true）容許 CMS 設定邊套劇免費開放。
- **廣告影片 CMS**：admin 頁「廣告管理」tab 可上傳 mp4、切啟用、刪除；`ads` 表（migration `c7d8e9f0a1b2`）＋ `python-multipart`。

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
