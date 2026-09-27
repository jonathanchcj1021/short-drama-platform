# 短劇平台 Web 前端

短劇平台 monorepo 的 Web 前端，使用 **Next.js 14（App Router）+ TypeScript（strict mode）**，並以**靜態匯出**方式部署至 GitHub Pages。

## 技術棧

- Next.js 14（App Router）
- TypeScript（strict mode）
- CSS Modules（無 Tailwind，零額外 CSS 建置鏈）
- 純用戶端 fetch 呼叫後端 API（不使用 Next.js API Routes）

## 目錄結構

```
web/
├── app/
│   ├── layout.tsx              # 根佈局，含 Navbar
│   ├── page.tsx                # 首頁（劇集列表 + 分類篩選）
│   ├── login/page.tsx          # 登入頁（手機號碼 + OTP）
│   ├── drama/[id]/page.tsx     # 劇集詳情（server wrapper）
│   ├── drama/[id]/DramaDetailClient.tsx
│   ├── play/[episodeId]/page.tsx        # 播放頁（server wrapper）
│   ├── play/[episodeId]/PlayClient.tsx
│   └── globals.css            # 全域樣式
├── components/
│   ├── Navbar.tsx
│   ├── DramaCard.tsx
│   ├── EpisodeList.tsx
│   └── ProtectedRoute.tsx
├── lib/
│   ├── apiClient.ts            # fetch 包裝（自帶 Authorization、401 跳轉）
│   └── auth.ts                 # token 管理（localStorage）
├── types/
│   └── index.ts                # Drama / Episode / Category / User / OTP 等型別
├── public/
│   └── favicon.ico
├── .env.example
├── .gitignore
├── next.config.js
└── tsconfig.json
```

## 環境變數

複製 `.env.example` 為 `.env.local` 並依後端位置調整：

```bash
cp .env.example .env.local
```

預設值：

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 啟動方式

```bash
# 安裝相依套件
npm install

# 開發模式（http://localhost:3000）
npm run dev

# 型別檢查
npx tsc --noEmit

# 產出靜態檔（輸出至 out/ 目錄）
npm run build

# 本機預覽靜態產物
npm run start
```

## 對應的後端 API

| 用途 | Method | Path |
| --- | --- | --- |
| 要求 OTP 驗證碼 | POST | `/auth/otp/request` |
| 驗證 OTP 登入 | POST | `/auth/otp/verify` |
| 分類列表 | GET | `/categories` |
| 劇集列表（可帶 `?category=`） | GET | `/dramas` |
| 劇集詳情 | GET | `/dramas/{id}` |
| 劇集觀看進度 | GET | `/dramas/{id}/progress` |
| 集數詳情 | GET | `/episodes/{id}` |
| 串流位址 | GET | `/episodes/{id}/stream` |
| 上報觀看進度 | POST | `/episodes/{id}/progress` |

## 部署說明

`next.config.js` 已設定：

- `output: 'export'`：產出純靜態檔至 `out/`
- `basePath` / `assetPrefix`：`/short-drama-platform`（GitHub Pages 專案頁路徑）
- `images.unoptimized: true`：靜態匯出不支援圖片最佳化
- `trailingSlash: true`：產生 `index.html` 以利 GitHub Pages 路由

> 注意：靜態匯出不支援伺服器端動態路由參數，因此 `/drama/[id]`、`/play/[episodeId]` 皆為 client component，路由參數由 `useParams()` 在瀏覽器端讀取。
