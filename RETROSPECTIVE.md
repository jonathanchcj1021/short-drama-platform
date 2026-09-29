# 開發檢討 — 點解之前幾輪「話修咗」用戶照樣唔得

日期：2026-09-29　版本：v1.0.0

## 一句講晒
之前嘅「修復」全部停喺**改 code + curl localhost 200**，冇做最後一公里：**後端冇重啟、Web 冇 build+部署、冇用真部署路徑驗證**。所以 repo 入面好似改咗，用戶見到嘅站仲係舊嘅／壞嘅。

## 逐個根因

### 1. 改完後端 code，uvicorn 冇重啟（或重啟錯版本）
- FastAPI 用 Python import cache，改完 `.py` 唔重啟 process，live 服務行緊嘅仲係舊 code。
- 中途更出現多個 process 同時 `pkill` 重啟，導致同一時間 localhost 同 tunnel 回唔同結果（race）。
- **根治**：改完必重啟 uvicorn，並**分別對 localhost 同 tunnel 同一 endpoint** 對比 response，確認行緊新版本。

### 2. Web 係靜態 export，改 code 唔 push 唔部署 = 用戶見唔到
- Next.js `output: 'export'` 要 `npm run build` → push → 等 GitHub Actions → 先至係 GitHub Pages 用戶見到嘅 bundle。
- 之前 agent 本地改咗、話 build 過，但冇行到部署呢步，用戶 reload 仲係舊 JS。
- **根治**：以部署後 `curl` 真實 GitHub Pages URL 確認新碼（footer v1.0.0、`auth-changed` 邏輯）真係上線，先算完。

### 3. 用 localhost curl 當驗證，但用戶行嘅係 github.io → tunnel
- localhost 通 ≠ 真站通。分別：CORS、basePath、Referer。
- **關鍵發現**：紅果 CDN 有 **Referer 防盗鏈**——直接將 qznovelvod URL 交畀 github.io 前端，browser 會帶 `Referer: github.io`，CDN 回 **403**。curl 唔帶 Referer 所以測試通，一上 browser 就黑畫面。
- **根治**：片源唔再直出 CDN，改由後端 `/episodes/{id}/media?token=` 代理轉發 Range（206），前端只 request 自己嘅 domain，繞過防盗鏈。

### 4. 修一個 bug 反佢個 unit test / 製造新 bug
- 改成 media proxy 之後，舊 test 仲斷言 `video_url == 上游 CDN URL`，CI 由綠轉紅——即「修咗播放但 break 咗測試」。
- **根治**：每改 API 契約，同步更新對應 test；本地行晒 `pytest` 先算。

## 今次點樣先算真係驗證過（唔再自我感覺良好）
- `qa_check.py` 經公開 tunnel 掃描，唔係 localhost：6/6 PASS，頭排三套劇 Range GET 回 `206 video/mp4`。
- `pytest`：12 passed。
- 部署站 index.html 實測含 `v1.0.0`。
- Refresh token 經 tunnel：200；冇 token 取片：401。
- **誠實交代**：GUI 人手 click-through（reload 後 Navbar、admin 頁進出）喺本環境做唔到，已喺 QA checklist 標做 ⚠️ 待確認，冇當佢 Pass。

## 下次 SOP（防再犯）
1. 後端改 code → 重啟 uvicorn → localhost 同 tunnel 對比。
2. Web 改 code → `npm run build` → push → 等 Actions 綠 → curl 真站確認新碼。
3. 驗證行**用戶真實路徑**（github.io → tunnel → media 代理），唔係齋 curl localhost。
4. 改 API 契約必同步更新 test，CI 要綠。
5. 唔好將「curl 200」當「browser 播到」。
