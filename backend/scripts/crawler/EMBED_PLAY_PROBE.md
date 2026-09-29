# 優酷官方 embed 播放器複測報告（iframe 方案）

> 複測日期：2026-09-29（HKT，香港 IP）。目的：驗證「優酷官方 iframe embed 播放器
> `player.youku.com/embed/{vid}`」可唔可以喺平台內直接播放正片。Server-side 抽片源已證實
> 唔可行（見 `YOUKU_PLAY_PROBE.md`），呢個係最後一條官方合法路線。
> 實測劇：**獵罪現場**（showId=`fdeb4785cd6b49bc8c9d`，24 集）、**千金丫環**
> （showId=`bfae219e943544dc8700`，30 集）、**春霆念未央**（showId=`dfaba505ba7544dd9dc1`，24 集）。
> 方法：真瀏覽器（Chrome）執行 JS 抽 vid，再用 curl + 瀏覽器驗證 embed 播放。全程
> **冇登入、冇繞 DRM／paywall**（embed 係優酷官方「分享」功能提供嘅 iframe）。

## 結論先行

**唔可以。** Embed 播放器出到真正片畫面，但**忠實反映優酷 paywall**：

| 內容層次 | 結果 |
|---|---|
| 免費試看集（benefitType=0，每劇頭 2–3 集） | 出到真實正片畫面，但只開放約 **35 秒試看**，前後夾廣告（約 50–73 秒前貼片 + 中貼片），角落長駐「看完整視頻」；撳「跳過廣告」會**跳去 `pay.youku.com/buy` 付費頁** |
| VIP 集（benefitType=1，頭 2–3 集之後全部） | **即時硬 VIP 牆**「該視頻僅限 VIP 會員觀看」，零畫面 |
| 控制組（34 秒宣傳剪片） | 出到首 frame，廣告後主片「加載中」，亦帶「看完整視頻」 |

平台 40 部優酷劇全部係同類內容（搜尋卡片全部帶「獨播／VIP」角標），所以 **embed 方案
救唔到「開唔到片」嘅投訴**。維持 v1.2.1 已有嘅「資料卡 · 未接片源」誠實標示，
**唔改任何代碼**。

---

## 逐步實測結果

### 1. 攞正片 vid —— 成功、可重現、全程唔使登入

1. **搜劇名拎 showId**：開 `https://so.youku.com/search/q_<劇名>`，等 JS 跑 6 秒，
   讀 `window.__INITIAL_DATA__`，遞迴搵同時有 `showId` + `tempTitle/titleDTO.displayName`
   + `cats` 含「短剧」嘅卡片。
2. **入劇集頁**：導航去 `https://v.youku.com/video?s=<showId>`，等 8 秒。頁面 302 到
   `v.youku.com/v_show/id_<第1集vid>.html`，title 已係「<劇名> 第1集 …」。
3. **抽 episode list**：`window.__INITIAL_DATA__` 入面搵 array，每個 item 同時有
   `action_value`（base64 vid，regex `^[A-Za-z0-9+/=]{8,}$`）、`rank`（集號）、
   `title`（「<劇名> 第N集」）、`episodeInfo.benefitType`（0=免費試看 / 1=VIP）。
   實際路徑三部劇都係 `moduleList[0].components[N].itemList`（N 因劇而異，用 regex 偵測最穩陣）。

**三部劇 78/78 集 vid 全部拎到**（24 + 30 + 24），免費試看 2/2/3 集，其餘 VIP。
完整清單見同目錄 `youku_embed_probe_vids.json`（每劇含 `drama_db_id`、`showId`、
`drama_page_url`、`ep1_url`、`episodes: [{rank, vid, benefitType}]`）。

### 2. curl 層測試 embed endpoint

`https://player.youku.com/embed/<vid>`（桌面 Chrome UA）→ **全部 HTTP 200、5164B**，
免費／VIP／promo 三種嘅 HTML 經 `diff` 證實完全一樣——embed endpoint 係通用 player 殼，
由 URL path 攞 vid 再 `new YKU.Player(...)`，**curl 層冇任何 per-vid block、冇地域／登入牆字樣**。
實際限制全部喺 JS player 入面，所以必須真瀏覽器驗證。

### 3. 瀏覽器層測試（真瀏覽器開 embed，等 JS 跑再截圖）

| 測試 vid | 劇／集 | benefitType | 瀏覽器畫面結果 | 截圖 |
|---|---|---|---|---|
| `XNjUxODI3NTg3Ng==` | 春霆念未央 第1集 | 0（免費） | **真正片畫面** 0:09/13:09（字幕「為了給在戰場犧牲的姐妹復仇」），長廣告 + 「看完整視頻」長駐 | `embed_probe_assets/embed_free_ep1_real_footage.png` |
| `XNjUyNjc5NDg1Ng==` | 春霆念未央 第4集 | 1（VIP） | 即時硬 VIP 牆「該視頻僅限 VIP 會員觀看」+ 橙色「開通VIP會員」 | `embed_probe_assets/embed_vip_ep4_hard_wall.png` |
| `XNjUyOTU5MzQxNg==` | 控制組：34 秒宣傳剪片 | — | 出到首 frame（0:00/0:34），廣告後主片「加載中」，亦帶「看完整視頻」 | `embed_probe_assets/embed_control_promo_frame.png` |
| `XNjU2MTQ3ODIyMA==` | 獵罪現場 第1集 | 0 | 同春霆免費集 pattern（前貼片→試看 ~35s→看完整視頻） | （同 pattern，未另存） |
| `XNTkwMDEzMjQ3Mg==` | 千金丫環 第1集 | 0 | 同上 pattern | （同 pattern，未另存） |

免費集實測細節：廣告播完後主內容喺 00:08/13:09 開始出，播到約 **00:35 就停**，
「看完整視頻」overlay 長駐；撳「跳過廣告」會將 embed 本身導航去
`pay.youku.com/buy/products.htm?from=ad`——即係無 VIP 用戶「跳廣告」= 去付費牆。

---

## 點解確認係 paywall 而唔係技術 block

1. **curl 層三種內容嘅 player 殼完全一樣**（5164B，`diff` 輸出為空）——embed endpoint
   冇做內容層過濾，限制係 JS player 按 vid 內容決定。
2. **免費集係「試看片段＋廣告＋看完整視頻」組合，撳跳廣告直接去 `pay.youku.com/buy`**
   ——係優酷官方付費轉化流程，唔係地域／登入 block。
3. **香港 IP 全程未見地域限制字樣**；VIP 牆係內容策略（內容標 VIP／獨播），唔係地域。

## 對平台 40 部優酷劇嘅影響

- **唔好 backfill episode video_url 指向 embed**：免費集會帶用戶去 paywall、VIP 集全硬牆，
  體驗比而家「資料卡 · 未接片源」更差，仲會誤導。
- 維持 v1.2.1 已有嘅「資料卡 · 未接片源」誠實標示，唔郁代碼。
- 已攞到嘅 78 集 vid（`youku_embed_probe_vids.json`）留底：將來若用戶想加「優酷站外
  跳轉／試看」功能可以重用（embed 本身係官方分享功能，屬合法用法）；Embed 播放器整
  體方案嘅實作規格（後端 `video_type` + 前端 iframe render）喺本次 session 產出過，
  需要時可照做。

## 重現方式

```bash
# 1) 攞 vid：真瀏覽器（唔係 curl）
#    so.youku.com/search/q_<劇名> → window.__INITIAL_DATA__ 搵 showId
#    v.youku.com/video?s=<showId> → __INITIAL_DATA__ 每集 action_value + benefitType
# 2) 測 embed（curl 層）
curl -s -o /tmp/embed.html -w "HTTP %{http_code}\n" \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" \
  "https://player.youku.com/embed/<vid>"
# 3) 測 embed（瀏覽器層）：真瀏覽器開 https://player.youku.com/embed/<vid>，
#    等 JS 跑 10 秒，截圖睇有冇真畫面／VIP 牆／「看完整視頻」
```

（探測只讀公開頁 + 官方 embed iframe，唔寫 DB、唔改其他檔案；瀏覽器動作之間有間隔。）
