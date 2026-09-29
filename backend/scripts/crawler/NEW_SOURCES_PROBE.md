# 快手星芒短劇 / 騰訊（v.qq.com・微視）短劇 公開網頁探測報告

> 探測日期：2026-09-29（HKT）。目的：評估呢兩個來源有冇**公開、免登入、可 SSR parse**
> 嘅網頁排行榜／片單，從而照 `hongguo.py` 模式寫爬蟲 adapter。
>
> **結論先行：兩個來源都唔可爬（app-only + robots 封鎖 + 簽名/DRM）。**
> 所以冇建立 `kuaishou.py` / `tencent.py` adapter —— 唔寫假嘢。

---

## 1. 快手星芒短劇（kuaishou.com）

### robots.txt（決定性封鎖）
`https://www.kuaishou.com/robots.txt` 內容結構：

```
User-agent: Baiduspider / Baiduspider-video / Googlebot / Sogou / 360Spider / bingbot / ...
Allow: /

User-agent: *
Disallow: /

Sitemap: https://www.kuaishou.com/sitemap.xml
```

→ **淨係開畀特定搜尋引擎 bot**；我哋爬蟲用 Chrome UA，落入 `User-agent: *`，
**全站（`/`）被禁爬**。即使連得上，按「尊重 robots.txt」嘅約束都唔應爬。

### 實際連線
- `curl https://www.kuaishou.com/` → `HTTP=000`，`Connection timed out after 30s`
  （TLS 連線都建立唔到；呢個網絡（HK）直接被丟棄／區域封鎖）。
- 對照：同一刻 `hongguoduanju.com` 係 HTTP 200 / 207KB —— 證明係站方封鎖，唔係本機網絡問題。

### 唯一嘅「快手短劇」網頁 = B 端後台
- `https://kdj.kuaishou.com/v2/portal`（快手短劇經營者管理平台）→ HTTP 200 但**只有 1235 bytes**，
  淨係 `<div id="root"></div>` + JS bundle，**完全冇 SSR 資料**，而且係創作者／運營後台，要登入，
  根本唔係消費片單。

### 小結
星芒短劇嘅消費側片單／播放**只存在於快手 App／小程序**。Web 冇公開熱播榜，
有 robots 全站禁爬，連線又被丟棄。**唔可爬，不寫 adapter。**

---

## 2. 騰訊短劇（v.qq.com 短劇頻道 / 微視）

### robots.txt
- `https://v.qq.com/robots.txt`：`User-agent: *` 只禁特定路徑（`/cover_v2/`、`/doki/`、
  `/biu/`、`/txp/`、`/wechat/`…），**冇全站禁**——所以問題唔喺 robots，而係內容本身唔 SSR。
- `https://weishi.qq.com/`：robots.txt 路徑直接返 SPA HTML，而且內嵌
  `<meta name="robots" content="none" />`（叫所有搜尋引擎唔收錄）。

### 冇公開短劇頻道／片單頁
- 試 `https://v.qq.com/channel/duanju`（同 `/shortdrama`、`/minidrama`）→ **302 → `v.qq.com/error.html`**
  （「那条视频不见了」）。Web 導航（電視劇/電影/綜藝/動漫…）根本冇「短劇」呢個入口。
- `https://v.qq.com/x/search/?q=短剧` → HTTP 200 但**只有 3211 bytes** shell，SSR 零條結果，
  冇任何 `/x/cover/<cid>.html` 連結（搜尋結果全部靠簽名 API 後端灌）。
- `https://film.video.qq.com/h5/short-play-vip/index.html`（豎屏短劇通）→ 9.7KB，
  係**訂閱付費營銷頁**（講「特惠開通」），冇劇集目錄、冇 cid 列表。

### 單部 cover 頁都唔 SSR metadata（抽查 `v.qq.com/x/cover/mzc002003kpyd2m.html`）
- HTTP 200 / 189KB，但：
  - `<title>` 係 generic **「腾讯视频」**，**冇劇名**；
  - `application/ld+json` = **0 個**；
  - HTML 入面**抽唔到** `title`/`episode_count`/`duration`/`playUrl`/`.mp4`；
  - 全文淨係 1 個 vid（當前集），**冇集數列表**；
  - 真實資料走 `window.__VINFO_DATA__` → client-side 動態 `_.onload` 簽名 API 先拎到；
  - player 設定可見 `demux2fmp4`、`enableP2P` —— 片源係 **DRM/signed fMP4**，唔係公開 MP4。

### 小結
騰訊短劇消費側喺 Web 冇公開排行榜/片單；單頁 metadata 要簽名 API，片源係 DRM。
微視 Web 係 SPA 兼 `robots:none`。**唔可爬，不寫 adapter。**

---

## 3. Smoke test 結果（實抓一頁 parse）

| 來源 | 實抓 URL | HTTP | 回傳大小 | parse 到劇 | 抽到片 URL |
|---|---|---|---|---|---|
| 紅果（對照，正常） | hongguoduanju.com/rank/hot-drama | 200 | 206,922 B | 正常有劇卡 | 頭幾集公開 |
| 快手 www.kuaishou.com | / | 000 | 0 B | 0（連唔上） | 0 |
| 快手 kdj 後台 | /v2/portal | 200 | 1,235 B | 0（SPA shell，B 端登入） | 0 |
| 騰訊頻道 | /channel/duanju | 302→error | — | 0（跳錯誤頁） | 0 |
| 騰訊搜尋 | /x/search/?q=短剧 | 200 | 3,211 B | 0（JS shell） | 0 |
| 騰訊 cover 頁 | /x/cover/mzc002003kpyd2m.html | 200 | 189,814 B | 0（title 只係「腾讯视频」） | 0（DRM signed fMP4） |
| 微視 | weishi.qq.com/ | 200 | SPA | 0（robots:none） | 0 |

**實際「抽到幾多部劇」：快手 0、騰訊 0。** 唔係 selector 寫錯，係頁面根本冇 SSR 內容。

## 4. 撞過嘅 anti-bot / 牆
- 快手：robots `* Disallow:/` + 連線層 timeout（疑似區域/反爬丟棄）；App 內仲有 `ns_token` 簽名機制（**冇去繞**）。
- 騰訊：vinfo 簽名 API、DRM/signed fMP4 player、搜尋與頻道全 SPA 後端灌資料；微視 `robots:none`。

## 5. 建議
- 呢兩條線暫時**唔好接 adapter**，避免寫出會回傳空陣列／假片 URL 嘅假爬蟲。
- 若日後真係要騰訊短劇 metadata，合法途徑係：騰訊開放平台／WeTV 官方 API、或授權合作；
  唔好用 headless browser 繞 vinfo 簽名或解 DRM。
- 快手若要收錄，考慮用官方星芒片單新聞稿（澎湃/界面）做**人工片單 metadata**，而非爬 kuaishou.com。
