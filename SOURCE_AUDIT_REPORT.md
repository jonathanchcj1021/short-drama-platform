# 40 部優酷短劇 · 片源審計總表（SOURCE AUDIT REPORT）

> 審計日期：2026-09-29（HKT）　|　範圍：DB drama_id 57–96 共 40 部優酷獨播短劇
> 片源原則：**只收優酷官方／認證頻道**（YOUKU English / YOUKU Mini Drama / YOUKU COSTUME / YOUKU ROMANCE / YOUKU SUSPENSE 等藍 V 認證號）或官方平台免費區；第三方搬運頻道一律唔收。
> 狀態定義：
> - **已接入** = 已建 episodes row、`source='youtube'`、可喺平台播放（今次示範 5 部）。
> - **可接入** = 官方 YouTube playlist 齊全，尚未建 DB（之後可照同一 seed script 模式接入）。
> - **潛在** = 有官方片源但有保留：後段集數 YouTube 設為 Members only（付費牆），或平台 SPA 爬唔到。
> - **無免費** = 搵唔到合法免費全集片源。

## 地區封鎖備註（重要）
優酷官方 YouTube 頻道所有影片描述都註明：**「部分地區（港／澳／台／東南亞）正片請移步優酷國際版 APP」**。本機（香港）實測：開官方 playlist 頁，YouTube 會顯示「系統已隐藏 N 个无法播放的视频」，絕大多數集數喺香港地區 iframe 會被地區封鎖（僅個別頭集如 EP01／EP02 可免費播放）。因此呢啲片源**對海外（美／加／英／東南亞以外）觀眾係合法免費**，但對香港訪客未必播到——已喺實測如實截圖記錄，冇隱瞞。

---

## 一、已接入（5 部，132 集）

### drama 67 · 锁爱三生（Circle of Love）— 24/24 集 ✅
- 頻道：YOUKU English-Get APP now　|　playlist：https://www.youtube.com/playlist?list=PLIPiKkS-FpK-zTWsxZO5xUAlAsUEFOl3K
- 每集 video id（watch?v=）：

| EP | video id | EP | video id |
|---|---|---|---|
|01|Mt_o6K9Y59Q|13|e5PHcB1S7Do|
|02|0e4PUE95gCk|14|tFCc6RnlOIs|
|03|FGbciRJfGz8|15|h9ybnZQRWA0|
|04|kVop_5QZ-cM|16|ws_jHn0n9RE|
|05|NJXTCPVjSSI|17|gHq2yLxeEDI|
|06|l-X8cA1yLAg|18|qgd3lQqi7cw|
|07|NViayK1R56A|19|BGf1clB_uq0|
|08|V7m8WNX1gxE|20|9WN3oWZ8LSY|
|09|ps5CNXOsgSo|21|4J0PVfqNpXM|
|10|RDNpQQwImv8|22|LPA6cWd9vqA|
|11|Dv4_TvQgkZ8|23|-Pfck_LVY64|
|12|pZQA65WpwVI|24|ydWeU4T8c1U|

### drama 60 · 我们在黑夜中相拥（Embrace in the Dark Night）— 24/24 集 ✅
- 頻道：YOUKU English-Get APP now　|　playlist：https://www.youtube.com/playlist?list=PLIPiKkS-FpK9bYBL2pbkmPeJ_BHwTuEDX（38 條＝24 正片＋預告／合輯，已剔除）

| EP | video id | EP | video id |
|---|---|---|---|
|01|BVPQhfRwfUI|13|MBQmm2iT9vI|
|02|wgiNonQtBuk|14|nZKjAefTdzw|
|03|y5imWTy-Ar4|15|W0pzz8paWq0|
|04|5HL-VsHjLY8|16|diUffz37z_s|
|05|RXkxQBlbaew|17|V9Sjs5MvUIc|
|06|guvDPT6SRr8|18|ZD6_NdmsIYI|
|07|zGXURF_vZvU|19|OVnlO6sxVFs|
|08|Ce4Av1mA7bk|20|kBzK7gntigo|
|09|_EzkSgZdheE|21|3KDRrUOsds4|
|10|luW_bo2-xTw|22|u9d8cHU4C8s|
|11|haKtlKAxl3s|23|t_acesr_SHA|
|12|iCxlyG-h3cA|24|tRH0SRLXaIU|

### drama 63 · 爱在天摇地动时（Undercover Affair）— 24/24 集 ✅
- 頻道：YOUKU English-Get APP now　|　playlist：https://www.youtube.com/playlist?list=PLIPiKkS-FpK9h3K-IncmKNfMmKM4TdqcM（24 條乾淨對應）

| EP | video id | EP | video id |
|---|---|---|---|
|01|ipcnW-W5Fkg|13|QxDn-y6Cvlk|
|02|CUdzltp7lP0|14|AD9SfEyvGwk|
|03|AB8a8hg7pLg|15|P5AwveWx2ls|
|04|y9DkouSH4to|16|VO0IrUUnhas|
|05|sqgkF2zc56E|17|JakhjyGSaLI|
|06|y5w-yVcpbSc|18|CEvc3e2oyPg|
|07|xpnhJGUndos|19|XNopXTrzHhQ|
|08|uLJQ-Qz348I|20|txjWFowCkpQ|
|09|A3MFb1ku3NY|21|tts4T1t7ch8|
|10|jafyALuXCJw|22|XsHU6NQKgPg|
|11|MTKYsnjCslg|23|olKLHOaFn0s|
|12|uVeDlU_RJ9c|24|94J4LOR1mZA|

### drama 64 · 永夜长明（Dawn is Breaking）— 30/30 集 ✅
- 頻道：YOUKU English-Get APP now　|　playlist：https://www.youtube.com/playlist?list=PLIPiKkS-FpK-BxGpxeLaoE3RK1-B27J2K（40 條＝30 正片＋預告／合輯，已剔除）

| EP | video id | EP | video id |
|---|---|---|---|
|01|6YYeJcdHos4|16|G451cOmMu14|
|02|rXl_g4_1O4s|17|78BUGN7wbMw|
|03|vawGay9YgFc|18|WQYgPqXxu0s|
|04|0sUb3_hR9ok|19|YSNfsYerNUY|
|05|z6MydktWpw0|20|_EWNCtfmVN8|
|06|Vs9aa4SJyEc|21|Z6PRnPZlQGU|
|07|oCCnEf_gEA4|22|zGVuGGLHnk4|
|08|45lv8Y1SRMI|23|Rz2uuoluMvE|
|09|5i-tVfTFX1c|24|t3ijLSiWkc8|
|10|ypbIF9XGhIY|25|RCEnLrOK2Nk|
|11|dEjyH7Gg_js|26|CrW7GBI1QD4|
|12|2jKJSKq-qlI|27|bvU6LqhG0nI|
|13|YMOgiymZf9Y|28|ixABUsYwTeM|
|14|l4414iJCE_U|29|rSlp4Sh6mdQ|
|15|h0HxHdwlxaQ|30|xTqe-h63puw|

### drama 66 · 千金丫环（Maid's Revenge）— 30/30 集 ✅
- 頻道：YOUKU Mini Drama-Get APP Now　|　playlist：https://www.youtube.com/playlist?list=PLogLib6e6DfRzv1GvGLaaa_0pgXhmiQ5-（39 條＝30 正片＋合輯／花絮，已剔除）

| EP | video id | EP | video id |
|---|---|---|---|
|01|ct0kqNJkfVg|16|3Mt6UyP-F1g|
|02|anoSHaeW5Q8|17|jrUvyWQ-quM|
|03|42h6S5TCNS4|18|lh1tqmhfqQU|
|04|JLVeIA8eB18|19|s8vtrmTPj9U|
|05|gfwYDNGBjF0|20|Df2gka3qP2Y|
|06|1rcXqEnIrxc|21|MLzYtWqBOa8|
|07|d-4Cu5Mukmw|22|ODD9Gc7dS5g|
|08|BULpIYb7smE|23|wuUwlWyu4WU|
|09|ad3tkkBjnJo|24|o_zcrMzkwl8|
|10|9Up9jwHOMl8|25|lePGarSHbsw|
|11|ZoknZ0CKS_U|26|ZesauPqe974|
|12|xtLnOTAVAKQ|27|noA-_BhcVOA|
|13|1ceXNXRpnLM|28|OfFfucmruC0|
|14|T3vGrnlRH2Y|29|3brK1vODJzI|
|15|8EBCFtonQBs|30|UnujCfuuk2s|

---

## 二、全 40 部總表

| ID | 劇名 | 優酷集數 | 片源平台 | URL（playlist／入口） | 免費集數 | 狀態 | 備註 |
|---|---|---|---|---|---|---|---|
|57|猎罪现场|24|YouTube|https://www.youtube.com/watch?v=_Wj70BemIcc（新劇，頻道片單）|24|可接入|YOUKU English，2026-09 新劇陸續上傳；暫無獨立 playlist|
|58|驸马小仵作|43|YouTube|https://www.youtube.com/@youkucostume|43|可接入|YOUKU COSTUME 官方古裝頻道；EP42=j8yn55zbtY8|
|59|炽热吸引|40|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK-utiBJpckNSMpyNUgLXQmG|40|可接入|YOUKU English，ENGDUB 全套 40 條|
|60|我们在黑夜中相拥|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK9bYBL2pbkmPeJ_BHwTuEDX|24|**已接入**|YOUKU English|
|61|少年歌行之天下无双|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK-hg8djybp-4zuLcpWsOekY|24|可接入|YOUKU English，28 條＝24 正片＋花絮|
|62|渡清欢|30|YouTube|https://www.youtube.com/playlist?list=PLdTpgsneunzopM4Hgh3xxGjklejDht0ps|30|可接入|YOUKU SHOW English，78 條＝30 正片＋多語配音版|
|63|爱在天摇地动时|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK9h3K-IncmKNfMmKM4TdqcM|24|**已接入**|YOUKU English|
|64|永夜长明|30|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK-BxGpxeLaoE3RK1-B27J2K|30|**已接入**|YOUKU English|
|65|黑夜中的她|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK8690Fc6kEg2rpEumYZyupg|24|可接入|YOUKU English，EP01=D1V8eJRDPl4|
|66|千金丫环|30|YouTube|https://www.youtube.com/playlist?list=PLogLib6e6DfRzv1GvGLaaa_0pgXhmiQ5-|30|**已接入**|YOUKU Mini Drama|
|67|锁爱三生|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK-zTWsxZO5xUAlAsUEFOl3K|24|**已接入**|YOUKU English|
|68|反诈·猎蜂者|29|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK8bX4VpzFQIm-2Pcw7GqjXK|前段|潛在|YOUKU SUSPENSE；後段集（至少 EP29）已設 Members only 付費牆|
|69|万万没想到 第一季|—|—|—|0|**無免費**|YouTube 官方無全套；B站只有個人搬運（不合規）|
|70|铁石心肠|24|YouTube|https://www.youtube.com/playlist?list=PLogLib6e6DfQY_VibSQdf7wxm9Zd3dLRP|24|可接入|YOUKU Mini Drama，25 條＝24 正片＋預告；EP01=faVqMEyfalc|
|71|非她不可|26|YouTube|https://www.youtube.com/playlist?list=PLK9tD0pLL-mNLoUV4eM0Bsgthz133bzbP|26|可接入|YOUKU Spanish 官方西語字幕全套 26 條|
|72|东北往事之大时代|42|—|—|0|**無免費**|本土化抗戰題材，未做海外 YouTube 發行|
|73|鹅绒雪|20|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK-xppu4uYnezRiEUK0YmgWz|20|可接入|YOUKU English，39 條＝20 正片＋精華/BTS；EP01=5EFs89zJexY|
|74|别跟姐姐撒野|20|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK_d2K7C8yFF6izQVytXlhGi|20|可接入|YOUKU English 2022 老劇全套；EP01=tO4TEeeM0D4|
|75|凤骨琉璃|62|爱奇艺|http://www.iqiyi.com/a_15ywxnj6d71.html|62|潛在|愛奇藝官方標註全程免費無角標；但 web 係 SPA，爬取需簽名 API/DRM，未接入|
|76|只是未婚夫的关系|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK_88g8Wdopm6Ta1nlFBwLrx|24|可接入|YOUKU English 全套 24 條；EP01=PZiaoeC3Fz4|
|77|锦绣倾城王妃不好惹|54|—|—|0|**無免費**|僅第三方盜錄/搬運，官方無 YouTube 全集|
|78|魔方游戏之罪杀|20|YouTube|https://www.youtube.com/playlist?list=PLATwx1z00Hsf9vKjmRVSgah0WxM5ErE0-|2|潛在|官方 playlist 只 EP01(B3-yuR4oHOk)/EP02(GtfO77S9FtU) 免費，其餘係預告＋會員專享|
|79|掌中独宠|24|YouTube|https://www.youtube.com/playlist?list=PLATwx1z00HscMoFxcivOBx4IvTglNn2iF|24|可接入|YOUKU 主頻道 MULTISUB，25 條；已抽 EP01–15|
|80|乘风而上的她|24|YouTube|https://www.youtube.com/playlist?list=PLogLib6e6DfT1raVpOfn32K718qY9RqbS|24|可接入|YOUKU Mini Drama 全套 24 條；已抽 EP01–15|
|81|她与谎言|20|YouTube|https://www.youtube.com/watch?v=Wd8N-EEU5Jk|20|可接入|YOUKU 主頻道 MULTISUB 全套；無單一 playlist，由 EP01 順藤摸瓜|
|82|契约新娘|24|YouTube|https://www.youtube.com/playlist?list=PLQv8mbTGfRH3tkShbfLOtjmP_XvyuxBcM|24|可接入|YOUKU COSTUME 26 條；已抽 EP01–14|
|83|青雀成凰|30|YouTube|https://www.youtube.com/playlist?list=PLATwx1z00Hsd3DrNpHle4TT2aOQEmgaeJ|30|可接入|YOUKU 主頻道 32 條；已抽 EP01–15|
|84|半城风月半城雪|24|YouTube|https://www.youtube.com/playlist?list=PLogLib6e6DfTfd1z30xCWBlKgv_51YpQp|24|可接入|YOUKU Mini Drama ENGSUB 全套；已抽 EP01＋EP10–24|
|85|步步为陷|30|YouTube|https://www.youtube.com/playlist?list=PLATwx1z00HsdGULbzQ2vODKqzOzDUFxmG|30|可接入|YOUKU 主頻道 32 條；已抽 EP01–15|
|86|向她逆光而来|26|YouTube|https://www.youtube.com/playlist?list=PLATwx1z00Hsdso31G6GvkGxrOnEl7gSgG|26|可接入|YOUKU 主頻道 27 條；已抽 EP01–15|
|87|璀璨的她|21|YouTube|https://www.youtube.com/playlist?list=PLATwx1z00Hsc7hEamGC1tu4kBk_cPyWhE|21|可接入|YOUKU 主頻道 24 條；注意混有會員專享重複版要過濾|
|88|君心藏不住|24|YouTube|https://www.youtube.com/watch?v=we1DD2tuVy0|24|可接入|YOUKU COSTUME/ROMANCE/Mini Drama 分集上傳；無單一乾淨 playlist|
|89|风月如雪|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK-tD_4BzXFe64U8Q0SYnanD|24|可接入|YOUKU English 30 條（部分多集合併）|
|90|王老敢与游击队|12|—|—|0|**無免費**|紅色抗戰獻禮題材，唔對海外發行 YouTube|
|91|与君行|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK_Aoezxnc6zXDwfBTBmsDay|23|可接入|YOUKU English 23 條（對應 24 集，或有 1 集合併）|
|92|妻不可欺|26|YouTube|https://www.youtube.com/watch?v=FnQk19mwm00|26|可接入|YOUKU 西語官方頻道，描述列 EP01–26 全套；無單一 playlist|
|93|假面真情|26|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK_kIPYKm9cMg31YFwKOCL1j|26|可接入|YOUKU English 27 條|
|94|染指|27|YouTube|https://www.youtube.com/playlist?list=PLbBcESCAiV7HWJQqM0n_c9-CElqARgXBw|27|可接入|YOUKU ROMANCE【FULL】全套 27 條|
|95|龙门诀之大漠风云变|30|—|—|0|**無免費**|武俠 AI 短劇，官方 YouTube 無全集|
|96|春霆念未央|24|YouTube|https://www.youtube.com/playlist?list=PLIPiKkS-FpK_i02FIPrVsSgG3yjI68YMb|24|可接入|YOUKU English 28 條；部分集為會員搶先|

---

## 三、統計
- **總數**：40 部優酷獨播短劇。
- **已接入**：5 部（60、63、64、66、67），合共 132 集，全部 `video_type='youtube'`。
- **可接入（官方 YouTube 齊全，未建 DB）**：約 28 部。
- **潛在未接**：3 部（68 后段 Members only、78 只得頭 2 集免費、75 愛奇藝免費但 SPA 爬唔到）。
- **真係冇合法免費片源**：5 部（69 万万没想到第一季、72 东北往事之大时代、77 锦绣倾城王妃不好惹、90 王老敢与游击队、95 龙门诀之大漠风云变）。
