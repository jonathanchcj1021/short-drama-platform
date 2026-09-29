# 優酷短劇「免費公開可播放片 URL」server-side 可拎性複測報告

> 複測日期：2026-09-29（HKT）。目的：重新驗證 `youku.py` 註解入面「優酷正片播放頁全部上 DRM／VIP／登入牆，
> server-side curl 拎唔到可播放片 URL」呢個結論仲成立唔成立。
> 實測劇：**春霆念未央**（showId=`dfaba505ba7544dd9dc1`，24 集）、**龙门诀之大漠风云变**
> （showId=`ecfb166535434f668568`，30 集）。用 `.venv/bin/python3` + httpx + 桌面 Chrome UA。

## 結論先行

**唔可以。** Server-side（純 curl／httpx，唔執行反爬 JS、唔開 headless browser）**拎唔到**任何免費公開可播放嘅
正片 m3u8／flv／mp4 URL。`youku.py` 現狀嘅 metadata-only 做法係誠實做法，**唔使改**。

唯一 server-side 拎到嘅「片」係搜尋卡片入面嘅 `previewId` —— 但實測係 **34 秒宣傳剪片**，唔係正片任何一集，
而且連呢條剪片嘅真實串流 URL 都唔喺 SSR HTML 入面（`videoUpsStream: null`），要經簽名 API 先拎到。

---

## 逐步實測結果

### 1. so.youku.com 搜尋頁（現有爬蟲來源）— 正常，200
- `https://so.youku.com/search/q_春霆念未央` → **HTTP 200，176 KB**，`__INITIAL_DATA__` 正常 parse。
- `https://so.youku.com/search/q_龙门诀之大漠风云变` → **HTTP 200，186 KB**，正常。
- 卡片除原有欄位外，仲有：
  - `showId`（hex，如 `dfaba505ba7544dd9dc1`）
  - `previewId`（base64，如 `XNjUyOTU5MzQxNg==`）
  - `episodeTotal` / `allVipEpisode:"0"` / `exclusive:1`

### 2. www.youku.com/play/showid_<showId>.html — 廢棄，302 跳首頁
- `https://www.youku.com/play/showid_dfaba505ba7544dd9dc1.html` →
  **HTTP 200 但 final = `https://www.youku.com/ku/webhome`**（302 被 follow）。
- `<title>` 係「优酷-热门独播剧集综艺电影在线观看」（通用首頁標題），**冇劇名、冇片源**。
- → 呢個 `showid_*.html` 形態已經唔係有效播放頁（crawler 而家寫嘅 `detail_url` 落地即跳首頁）。

### 3. v.youku.com/v_show/id_<previewId>.html — 200，但係 34 秒宣傳 clip，冇 SSR 片源
- `https://v.youku.com/v_show/id_XNjUyOTU5MzQxNg==.html` → **HTTP 200，391 KB**。
- `<title>` =「沈念陆岳霆阳台上跳舞，太甜蜜啦-电视剧-高清完整正版视频在线观看-优酷」。
- 拆 `__INITIAL_DATA__`（brace-balance 切，216 KB）：
  - `duration: 34.24` → **呢條片只有 34 秒，係宣傳剪片**，唔係正片第 1 集。
  - `streamTypes:["flvhd","hd","hd2","hd3"]` 淨係畫質標籤；
    **`videoUpsStream: null`** → SSR 完全冇真實串流 URL。
  - `paid:0`（呢條 clip 本身免費），但同時有 `crmFreqList.vipPreviewInProgress`、
    `trial_buy_vip` 等 VIP 收費牆 UI 設定。
  - 全文掃 m3u8／mp4／flv：**0 個命中**；撞到 `DRM`／licenseServer 字樣。
  - 頁面入面 `id_XXX==` 形式 vid **只得呢一個 preview clip 自己** → **冇正片 episode list**
    （集數列表係 client-side 經簽名 API 先載入）。

### 4. m.youku.com/video/id_<previewId>.html（手機 H5）— 同樣冇片源
- 桌面 UA 換 iPhone Safari UA，→ **HTTP 200，120 KB**，title 同上。
- 一樣 `videoUpsStream: null`，m3u8／mp4／flv **0 命中**。

### 5. 串流 API：ups.youku.com/ups/get.json — 要簽名，裸 curl 被拒
- `https://ups.youku.com/ups/get.json?vid=<previewId>`（冇參數）→
  **HTTP 200 但 body 323B，`{"error":{"code":-6001,"note":"ccode参数错误"}}`**。
- 帶幾個猜測 web/h5 ccode（`d6d4b0e47a524d9b` 等）+ warmup cookie → **全部一樣 -6001**。
- 而且裸 GET v_show 頁**完全冇派 utid cookie**（只 set `isI18n=false`）；
  utid／acs token 係 Youku 反爬 JS（mtop 簽名）跑出嚟先有，curl 行唔到。
- 舊 endpoint `https://play.youku.com/play/get.json?vid=...&ct=10` → **HTTP 404**（已廢棄）。

---

## 點解確認係 DRM／VIP／簽名牆
1. **SSR 層**（桌面 v.youku + 手機 m.youku）兩邊都係 `videoUpsStream: null`，HTML 零 m3u8/mp4/flv ——
   片源唔係寫喺首屏 SSR，係 client-side 載入。
2. **串流層**唯一 endpoint `ups.youku.com/ups/get.json` 要有效 `ccode`（官方 player build 綁定）
   + `utid`（反爬 JS 鑄造）；裸 httpx 直接 `-6001 ccode参数错误`，連 utid cookie 都攞唔到。
3. **內容層**頁面帶 DRM/licenseServer 字樣 + VIP 試看／開通會員 paywall 設定。
4. **集數層** SSR 連正片 episode list 都冇，淨係一個 34 秒宣傳 clip。

呢啲全部同 yt-dlp／公開抓取實踐一致：優酷片源要逆向 mtop 簽名＋解 DRM，**唔係 server-side SSR parse 範疇**。

## 對現有 40 部 youku 劇嘅影響
- 唔使 backfill episode video_url —— 因為根本冇公開免費正片 URL 可以填，填咗都係假。
- `youku.py` 維持 metadata-only 正確。唯一可以順手改善嘅係：現有 `detail_url`
  （`www.youku.com/play/showid_<showId>.html`）落地會跳首頁；若要俾用戶一個真打得開嘅連結，
  可考慮改成 `https://so.youku.com/search/q_<劇名>`（搜尋結果頁有劇卡＋播放入口），
  但呢個係 UX 細節，唔係片源問題，今次唔郁。
- UI 「資料卡·未接片源」標示由另一個 Agent 跟進，屬預期做法。

## 重現方式
```bash
cd /Users/jc/short-drama-platform/backend
PYTHONPATH=. .venv/bin/python3 scripts/crawler/_probe_youku_play.py
```
（腳本只讀公開頁面，唔寫 DB、唔改其他檔案；request 之間 sleep 0.8–1s。）
