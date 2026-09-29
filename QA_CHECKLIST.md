# QA 測試 Checklist

**最新版本：** v1.0.0
**更新日期：** 2026-09-29
**負責：** QA / 研發小組

---

## 測試環境

| 項目 | 值 |
|---|---|
| 正式站 | https://jonathanchcj1021.github.io/short-drama-platform/ |
| 後端 | FastAPI :8000（cloudflared tunnel） |
| 測試帳號 | `85263106930` / `drama2026`（admin） |
| 一般用戶 | `webuser@test.com` / `webpass123` |

---

## 1. 登入流程

- [ ] 開首頁，未登入狀態顯示「登入」按鈕
- [ ] 入 `/login`，見到帳號密碼 form + Google 按鈕
- [ ] **冇** OTP / 手機驗證碼 tab
- [ ] 輸入正確帳密 → 跳到首頁，Navbar 顯示「管理」+「登出」
- [ ] 輸入錯密碼 → 顯示錯誤訊息
- [ ] 註冊新帳號 → 自動登入
- [ ] **記住登入**：登入後關 browser tab 再開，仲係登入狀態（唔使再入密碼）
- [ ] Access token 過期（15分鐘）後自動 refresh，唔會踢返 login 頁

## 2. 首頁

- [ ] 顯示劇集 grid，直版海報 9:16
- [ ] 每套劇標示「📱 紅果短劇」來源 badge
- [ ] 分類 chips（全部/武俠/都市/玄幻...）撳落去會 filter
- [ ] 冇封面嘅劇有漸層色代替
- [ ] 精選橫幅顯示最新劇

## 3. 劇集詳情

- [ ] 撳劇集卡 → 入到詳情頁
- [ ] 顯示劇名、分類、集數、簡介
- [ ] 集數列表顯示
- [ ] 撳第一集 → 入到播放頁

## 4. 影片播放

- [ ] 播放器載入唔會黑畫面卡死
- [ ] **真片可播**：有 CDN URL 嘅集數可以 play（HTTP 206）
- [ ] URL 過期時自動即時重簽（stream endpoint）
- [ ] 冇片嘅集數顯示「敬請期待」，唔好播無關畫面
- [ ] 上一集 / 下一集按鈕 work

## 5. CMS 管理後台

- [ ] Admin 先入到 `/admin`
- [ ] 可以新增 / 編輯 / 刪除劇集
- [ ] 可以新增分類
- [ ] 一般用戶入唔到 `/admin`

## 6. API 健康檢查

執行：
```bash
cd backend && DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" .venv/bin/python scripts/qa_check.py
```
預期：
- Login 成功
- 至少 1 集 `206 Partial Content`（真片可播）

## 7. 部署檢查

- [ ] `git log` 最新 commit 已 push
- [ ] GitHub Actions 綠色
- [ ] 線上版本係最新（hard reload 見到新 UI / 新功能）
- [ ] `CHANGELOG.md` 已更新

---

## 已知問題（Known Issues）

| 問題 | 狀態 | 原因 |
|---|---|---|
| Login 記唔住 | ⚠️ 部分瀏覽器 | 內建瀏覽器關 tab 清 localStorage；Safari/Chrome 正常 |
| CDN URL 過期 | ✅ 已修 | stream endpoint 即時重簽 |
| 第4集起冇片 | ℹ️ 預期 | 紅果要登入先有，我哋只公開頭免費集 |
| Google SSO | ⏳ 未接 | 缺 OAuth Client ID |
