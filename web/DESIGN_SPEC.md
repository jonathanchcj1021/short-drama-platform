# 短劇聚合平台 — 設計規範（UI Design Spec）

> 版本：v1.0　|　適用範圍：`web/`（Next.js 14 + TypeScript + CSS Modules）與 `android/`（Kotlin + Jetpack Compose）
> 目標：將現有「純色 flat 深色」升級為**影院級深色質感**，兩端共用同一套設計語言。
> 本文件為單一來源（single source of truth），工程師可直接照實作，不需再回問細節。

---

## 0. 設計理念與硬約束

### 0.1 設計關鍵字
- **影院暗色（Cinematic Dark）**：接近黑的多層背景，唔再係單一 `#141418`。
- **海報至上（Poster-first）**：劇集封面 3:4 係視覺重心，卡片以圖為主、文字壓 gradient 上。
- **層次感**：用漸層、細邊框、極輕玻璃擬態（glassmorphism）、柔和陰影堆出深度，拒絕 flat 純色。
- **明確字型層級**：標題／副標／內文／caption 一眼可分；大標改用襯线體（Noto Serif TC）營造海報感。
- **克制的微互動**：hover 浮起＋圖片微放大＋陰影加深，transition 統一時長與曲線。

### 0.2 唔可以破壞嘅硬約束（實作前必讀）
1. 路由維持查詢參數模式：`/drama/?id=1`、`/play/?episode=1`，**唔好**改動態路由。
2. 唔好改 `lib/apiClient.ts` 嘅 API 合約與 fetch 邏輯；新視覺只係 presentation 層。
3. 登入頁必須保留 **Google SSO + 電話 OTP** 兩條流程。
4. 分類名顯示統一用 `drama.category?.name ?? drama.categoryName ?? '未分類'`。
5. 一律用 **CSS Modules**，唔好引入 Tailwind 或任何 CSS framework。
6. `next.config.js` 維持 `output: 'export'` + `basePath`，唔好動。
7. UI 字串一律**繁體中文**。

---

## 1. Design Tokens（CSS custom properties）

以下整段可直接貼入 `web/app/globals.css` 嘅 `:root {}`。所有元件與頁面只准引用 token，唔准再寫死色碼／間距。

```css
:root {
  /* ===== 背景階層（由深到淺） ===== */
  --color-bg-deep:        #07070B;   /* 最外層／影片外圍／hero 最深處 */
  --color-bg-primary:     #0B0B10;   /* 頁面底色（body） */
  --color-bg-secondary:   #121219;    /* section 襯底、hero 漸層中層 */
  --color-surface:        #16161E;    /* 卡片、面板預設面 */
  --color-surface-raised: #1E1E28;   /* hover、浮起元素、導覽列面、輸入框底 */
  --color-surface-sunken: #0E0E14;   /* 嵌入容器（輸入框於淺卡上時） */

  /* ===== 邊框（半透明白疊喺深色上） ===== */
  --color-border-subtle:  rgba(255, 255, 255, 0.06);
  --color-border-default: rgba(255, 255, 255, 0.10);
  --color-border-strong: rgba(255, 255, 255, 0.18);

  /* ===== 主品牌 accent（暖紅） ===== */
  --color-accent:        #E63846;   /* CTA、active tab、強調 */
  --color-accent-hover:  #F04554;   /* hover 略亮 */
  --color-accent-press:  #C42735;   /* 按下略深 */
  --color-accent-soft:   rgba(230, 56, 70, 0.14);  /* 柔色底：選中 chip、tag */
  --color-accent-glow:   rgba(230, 56, 70, 0.35);  /* CTA 發光陰影 */

  /* ===== 次要 accent（琥珀金，僅「熱門／精選」標記用） ===== */
  --color-gold:       #F5B942;
  --color-gold-soft:  rgba(245, 185, 66, 0.16);

  /* ===== 文字 ===== */
  --color-text-primary:   #F5F5F7;   /* 標題 */
  --color-text-secondary: #A6A6B2;   /* 副標、內文次要 */
  --color-text-tertiary:  #6E6E7A;   /* caption、placeholder */
  --color-text-disabled:  #4A4A55;   /* disabled */
  --color-text-on-accent: #FFFFFF;   /* 紅底上嘅字 */

  /* ===== 語意色 ===== */
  --color-success:      #3DD68C;
  --color-success-soft: rgba(61, 214, 140, 0.14);
  --color-error:        #FF5C6C;
  --color-error-soft:   rgba(255, 92, 108, 0.12);
  --color-warning:      #FBBF24;
  --color-info:         #5EA8FF;

  /* ===== 漸層（見 §4 用途講解） ===== */
  --gradient-accent:       linear-gradient(135deg, #F04554 0%, #C42735 100%);
  --gradient-card-scrim:   linear-gradient(180deg, rgba(0,0,0,0) 35%, rgba(0,0,0,0.88) 100%);
  --gradient-hero-scrim-x: linear-gradient(90deg, rgba(7,7,11,0.92) 0%, rgba(7,7,11,0.55) 45%, rgba(7,7,11,0) 100%);
  --gradient-hero-bottom:  linear-gradient(180deg, rgba(11,11,16,0) 0%, var(--color-bg-primary) 100%);
  --gradient-surface:      linear-gradient(180deg, #1C1C26 0%, #16161E 100%);
  --gradient-nav:          linear-gradient(180deg, rgba(11,11,16,0.85) 0%, rgba(11,11,16,0.60) 100%);

  /* ===== 圓角 ===== */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 10px;   /* 卡片、按鈕、輸入框 */
  --radius-lg: 16px;   /* 大面板、登入卡、影片 */
  --radius-xl: 22px;
  --radius-full: 999px;

  /* ===== 陰影 ===== */
  --shadow-sm:   0 1px 2px rgba(0, 0, 0, 0.35);
  --shadow-md:   0 6px 20px rgba(0, 0, 0, 0.40);
  --shadow-lg:   0 16px 40px rgba(0, 0, 0, 0.50);
  --shadow-xl:   0 28px 70px rgba(0, 0, 0, 0.60);
  --shadow-accent: 0 10px 30px rgba(230, 56, 70, 0.35);
  --shadow-glass: inset 0 1px 0 rgba(255,255,255,0.06), 0 8px 30px rgba(0,0,0,0.45);

  /* ===== 間距（4px base grid） ===== */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-20: 80px;

  /* ===== 字型家族 ===== */
  --font-sans:   'Noto Sans TC', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 'PingFang TC', 'Hiragino Sans TC', 'Microsoft JhengHei', Roboto, sans-serif;
  --font-display:'Noto Serif TC', 'Songti TC', 'PMingLiU', serif;

  /* ===== 字型級距 ===== */
  --font-size-xs: 11px;
  --font-size-sm: 13px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
  --font-size-2xl: 22px;
  --font-size-3xl: 28px;
  --font-size-4xl: 36px;
  --font-size-display: clamp(28px, 4.5vw, 48px);

  --line-height-tight:   1.2;
  --line-height-snug:    1.4;
  --line-height-normal:  1.6;
  --line-height-relaxed: 1.75;

  --weight-regular:  400;
  --weight-medium:   500;
  --weight-semibold: 600;
  --weight-bold:     700;

  /* ===== 動態 ===== */
  --motion-fast: 150ms;
  --motion-base: 250ms;
  --motion-slow: 400ms;
  --ease-out:    cubic-bezier(0.16, 1, 0.3, 1);   /* easeOutExpo，入場／浮起 */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* 輕微 overshoot，hover pop */

  /* ===== 版面配置 ===== */
  --container-max: 1280px;
  --container-pad-x: 24px;
  --nav-height: 60px;
}
```

> **字體載入建議**：`layout.tsx` 的 `<head>` 加 Google Fonts（Noto Sans TC 400/500/700 + Noto Serif TC 700），例如
> `<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@700&display=swap" rel="stylesheet">`。
> 離線／無網路時會自動 fallback 到系統字型，唔影響功能。

---

## 2. Typography Scale

| 層級 | token | size | weight | line-height | 用途 |
|---|---|---|---|---|---|
| Display | `--font-size-display` | clamp(28→48px) | 700（`--font-display` 襯線） | 1.2 | 詳情頁大標、hero 標題 |
| H1 | `--font-size-3xl` | 28px | 700 | 1.25 | 頁面主標、登入「歡迎回來」 |
| H2 | `--font-size-2xl` | 22px | 600 | 1.3 | 區段標題「集數列表」 |
| H3 | `--font-size-lg` | 16px | 600 | 1.4 | 卡片標題、影片標題 |
| Body L | `--font-size-lg` | 16px | 400 | 1.6 | 輸入框文字 |
| Body | `--font-size-md` | 14px | 400 | 1.6 | 內文、meta |
| Body S | `--font-size-sm` | 13px | 400 | 1.5 | 次要說明、按鈕輔助 |
| Caption | `--font-size-xs` | 11px | 500 | 1.4 | badge、chip、標籤 |
| Button | `--font-size-md` | 14–15px | 600 | 1 | 按鈕文字（primary 用 15px/600） |

規則：
- 標題一律用 `--color-text-primary`，永遠唔好用純 `#fff` 死白。
- 內文用 `--color-text-secondary`，caption／placeholder 用 `--color-text-tertiary`。
- 卡片標題**最多 2 行**：`display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;`。
- 詳情頁大標與 hero 標題用 `var(--font-display)` 襯線；其餘全部 `var(--font-sans)`。

---

## 3. 顏色系統逐項用途

| 用途 | 色 | 說明 |
|---|---|---|
| 頁面底色 | `--color-bg-primary` | body 背景；hero 漸層最終收埋落此色 |
| section 襯底 | `--color-bg-secondary` | 偶爾做內容區細微色差，唔主動大面積用 |
| 卡片面 | `--color-surface` | DramaCard／EpisodeItem／登入卡預設 |
| 浮起面 | `--color-surface-raised` | hover 卡片、導覽列、輸入框底 |
| 主 accent 紅 | `--color-accent` | 主 CTA、active tab、目前集數、強調數字 |
| accent 漸層 | `--gradient-accent` | 主按鈕、active pill（取代純紅色塊） |
| 琥珀金 | `--color-gold` | 僅「熱門／精選」閃標；唔好濫用 |
| 成功綠 | `--color-success` | 已觀看、「上次看到」提示 |
| 錯誤紅 | `--color-error` | 表單錯誤、載入失敗（比品牌紅偏鮮，避免同 CTA 混淆） |
| 文字三階 | primary/secondary/tertiary | 見 §2 |

**漸層用途清單**：
- `--gradient-card-scrim`：劇集卡封面底部壓暗，令白色標題可读。
- `--gradient-hero-scrim-x` + `--gradient-hero-bottom`：首頁 hero 橫幅左／下兩邊壓暗。
- `--gradient-accent`：所有 primary 按鈕。
- `--gradient-surface`：登入卡等大面板由上到下細微明暗，增加立體感。
- `--gradient-nav`：頂列玻璃漸層。

---

## 4. 全域基礎（globals.css 更新）

除 `:root` tokens 外，`globals.css` 改為：

```css
* { box-sizing: border-box; }

html, body {
  margin: 0; padding: 0;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* 背景最外圍可加極淡暖色暈，營造影院氣氛（可選） */
body {
  background:
    radial-gradient(1200px 600px at 80% -10%, rgba(230,56,70,0.08), transparent 60%),
    var(--color-bg-primary);
  background-attachment: fixed;
}

a { color: inherit; text-decoration: none; }
button { font-family: inherit; }

::selection { background: var(--color-accent-soft); color: var(--color-text-primary); }

/* 深色捲軸 */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: #2c2c38; border-radius: 999px; border: 2px solid var(--color-bg-primary); }
::-webkit-scrollbar-track { background: transparent; }

/* 全域 focus 可見（無障礙） */
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* 容器：寬度 1280、左右 padding 24 */
.container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: var(--spacing-6) var(--container-pad-x) var(--spacing-16);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

---

## 5. 組件設計 Spec

### 5.1 Navbar（`components/Navbar.tsx`）

**定位**：sticky 頂列，玻璃擬態。

- 結構：`<header>` sticky `top:0`，`z-index:100`，高度 `var(--nav-height)`（60px）。
- 背景：`background: var(--gradient-nav); backdrop-filter: blur(16px) saturate(140%); -webkit-backdrop-filter: blur(16px) saturate(140%);`，底部 `border-bottom: 1px solid var(--color-border-subtle)`。
- 內層 `.inner`：`max-width: var(--container-max); margin:0 auto; padding: 0 var(--container-pad-x); height:100%; display:flex; align-items:center; justify-content:space-between;`
- Brand：
  - 左側加一個 24×24 圓角 6px 紅色漸層方塊（`var(--gradient-accent)`）做 logo mark，旁邊字「短劇平台」用 `--font-display`、18px、700、`--color-text-primary`。
  - hover 時 mark 略放大（`transform: scale(1.05)`，spring curve）。
- 右側：
  - 未登入：`登入` 按鈕 = `var(--gradient-accent)`、白字、`--radius-full`、padding `8px 18px`、font-weight 600；hover 加 `var(--shadow-accent)` 並略向上 1px。
  - 已登入：手機號用 `--color-text-secondary`、13px；`登出` = ghost 按鈕（透明底、`1px solid var(--color-border-default)`、`--radius-full`、padding `7px 16px`），hover 背景 `--color-surface-raised`。
- **Responsive**：手機（<640px）左右 padding 縮到 16px，brand 字縮到 17px，手機號縮到 12px 或省略長號碼。

### 5.2 DramaCard（`components/DramaCard.tsx`）— 視覺重心

改為**海報式**：封面即卡片主體，文字壓喺封面底部漸層上，唔再有下方獨立灰色 body。

- 結構：外層 `<Link>`，`position:relative`、`border-radius: var(--radius-md)`（10px）、`overflow:hidden`、`display:block`、`aspect-ratio: 3/4`。
- 封面 `<img>`：`width:100%; height:100%; object-fit:cover; display:block; transition: transform var(--motion-slow) var(--ease-out);`
- 漸層 scrim：封面內層疊一層 `position:absolute; inset:0; background: var(--gradient-card-scrim);`。
- Hover 狀態：
  - 外層：`transform: translateY(-6px) scale(1.01); box-shadow: var(--shadow-xl); border: 1px solid var(--color-border-strong);`
  - 圖片：`transform: scale(1.06);`（圖片微放大營造推近感）。
  - 陰影由 `--shadow-md` 升到 `--shadow-xl`。
  - transition：`transform var(--motion-base) var(--ease-out), box-shadow var(--motion-base) var(--ease-out);`
- 頂左分類 chip：`position:absolute; top:10px; left:10px;` 玻璃膠囊：`background: rgba(0,0,0,0.5); backdrop-filter: blur(8px); padding: 3px 10px; border-radius: var(--radius-full); font-size: var(--font-size-xs); color: var(--color-text-primary);` 內容用 `drama.category?.name ?? drama.categoryName ?? '未分類'`。
- 底部文字區：`position:absolute; left:0; right:0; bottom:0; padding: 12px 14px 14px;`
  - 標題：15px、600、白、最多 2 行 clamp。
  - 標題下一列（6px gap）：一個 6×6 圓點（`--color-accent`）+ `${episodeCount} 集`，12px、`--color-text-secondary`。
- Hover 正中間顯示播放鈕：一個 48px 圓形玻璃按鈕（`background: rgba(230,56,70,0.9); backdrop-filter: blur(8px);`），內有 ▶ 圖示；預設 `opacity:0; transform: scale(0.8);`，卡片 hover 時 `opacity:1; transform: scale(1)`（spring curve）。手機無 hover，常顯示淡一點（opacity 0.6）。
- 無封面 placeholder：將現有 inline SVG 改為漸層底（`linear-gradient(135deg,#22222e,#16161e)`）+ 置中 drama title（`--color-text-tertiary`、14px），唔好再用 flat `#3a3a44`。
- Focus-visible：`outline: 2px solid var(--color-accent); outline-offset: 3px;`

### 5.3 EpisodeList（`components/EpisodeList.tsx`）

- 外層 `<ul>`：`list-style:none; margin:0; padding:0; display:grid; grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); gap: var(--spacing-3);`
- 每個 `<a class=item>`：
  - `background: var(--color-surface); border:1px solid var(--color-border-subtle); border-radius: var(--radius-md); padding: 14px; display:flex; flex-direction:column; gap:6px; transition: all var(--motion-fast) var(--ease-out);`
  - Hover：`background: var(--color-surface-raised); border-color: var(--color-border-default); transform: translateY(-2px);`
- 「第 N 集」：13px、600、`--color-accent`。
- 集名：14px、`--color-text-secondary`、單行 ellipsis。
- 目前播放集（`.current`）：`background: var(--color-accent-soft); border-color: var(--color-accent);`，左邊加 3px 紅色 side bar（用 `box-shadow: inset 3px 0 0 var(--color-accent);`）。
- 已觀看（`.watched`）：12px、`--color-success`，前面加一個 ✓ 小圖示。
- Empty：`尚無集數`，`--color-text-tertiary`、置中 padding。

### 5.4 ProtectedRoute（`components/ProtectedRoute.tsx`）

- 取代純文字「載入中…」為**置中 spinner**：
  - 容器：`min-height: 100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; background: var(--color-bg-primary);`
  - Spinner：40px 圓環，`border: 3px solid var(--color-border-default); border-top-color: var(--color-accent); border-radius:50%; animation: spin 0.8s linear infinite;`
  - 文字：`--color-text-secondary`、14px（「載入中…」／「即將跳轉登入頁…」）。
- 加 keyframes：`@keyframes spin { to { transform: rotate(360deg); } }`。

---

## 6. 頁面設計 Spec

### 6.1 Home（`app/page.tsx`）

**Hero 區（新增，presentation-only，唔改 fetch）**：
- 條件：`!loading && !error && dramas.length > 0` 時，取 `dramas[0]` 做精選。
- 結構：全寬 `<section class=hero>`，高度桌面 420px／手機 260px。
- 背景：精選封面 `position:absolute; inset:0; object-fit:cover;`，上面疊 `--gradient-hero-scrim-x`（橫向）+ `--gradient-hero-bottom`（收埋落頁底色）。
- 內容（左对齐，垂直置中）：
  - 分類膠囊（玻璃底）。
  - 大標題：精選劇名，`var(--font-display)`、`--font-size-display`、白、最多 2 行。
  - 簡介：`--color-text-secondary`、最多 2 行 clamp、max-width 560px。
  - CTA 列：主鈕「▶ 立即觀看」→ `/drama/?id={id}`（`var(--gradient-accent)`、白字、`--radius-full`、padding 12px 28px、600）；次鈕「查看詳情」ghost 按鈕。
- Hero 與下方 grid 之間留 `--spacing-10`。

**分類 Tabs**：
- `.tabs`：`display:flex; flex-wrap:wrap; gap: var(--spacing-2); margin-bottom: var(--spacing-6);`
- 膠囊 `.tab`：透明底、`1px solid var(--color-border-default)`、`--color-text-secondary`、padding `8px 18px`、`--radius-full`、14px。
- Hover：border 變 `--color-border-strong`、文字變 primary。
- Active `.tabActive`：`var(--gradient-accent)` 底、白字、border 透明、`box-shadow: var(--shadow-accent)`。
- 過場：`transition: all var(--motion-fast) var(--ease-out);`

**Grid**：
- `.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(168px, 1fr)); gap: var(--spacing-5); }`
- 手機（<640px）：gap 縮到 `--spacing-3`，自然變 2 欄。

### 6.2 Login（`app/login/page.tsx`）

- 背景：`--color-bg-primary` + 頂部極淡紅色 radial glow（見 globals body）。
- 外層 `.wrap`：`min-height: calc(100vh - var(--nav-height)); display:flex; align-items:center; justify-content:center; padding: var(--spacing-8) var(--spacing-4);`
- 卡片 `.card`：
  - `width:100%; max-width:400px; background: var(--gradient-surface); border:1px solid var(--color-border-default); border-radius: var(--radius-lg); padding: 40px 36px; box-shadow: var(--shadow-xl); backdrop-filter: blur(12px);`
- 標題「歡迎回來」：`var(--font-display)`、26px、700；副標「電話驗證碼 或 Google 登入」：`--color-text-secondary`、14px。
- Google 按鈕：白底（#fff）、黑字、左邊加 Google「G」彩色 SVG icon、`--radius-md`、padding 13px、hover 略浮起（`translateY(-1px)` + `--shadow-md`）、disabled 透明度 0.6。
- 分隔線 `.divider`：左右兩條 1px 線（`--color-border-subtle`）中間夾「或用手機號碼」13px `--color-text-tertiary`，用 flex + `flex:1` 線條。
- 輸入框 `.input`：
  - `background: var(--color-surface-sunken); border:1px solid var(--color-border-default); border-radius: var(--radius-md); padding: 12px 14px; color: var(--color-text-primary); font-size: 16px; transition: border-color var(--motion-fast), box-shadow var(--motion-fast);`
  - Focus：`border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-soft); outline:none;`
  - label：13px、`--color-text-secondary`、下方 6px gap。
- Primary 按鈕（發送驗證碼／驗證登入）：`var(--gradient-accent)`、白字、600、`--radius-md`、padding 13px、hover 加 `--shadow-accent`、active 用 `--color-accent-press`。
- 重發 ghost 鈕：透明、`--color-text-tertiary`、13px、hover 變 secondary。
- 錯誤訊息：error 色、加 `--color-error-soft` 底膠囊（padding 8px 12px、`--radius-sm`）。
- **Responsive**：手機 card padding 改 `28px 22px`，左右 margin 16px。

### 6.3 DramaDetail（`app/drama/DramaDetailClient.tsx`）

- 整體：`.container`，頂部 hero header。
- Header `.header`：`display:flex; gap: var(--spacing-6); margin-bottom: var(--spacing-10); align-items:flex-end;`
  - 可選：header 背後加一個極淡 radial 紅光（`::before` 絕對定位）增加影院感。
- 海報 `.cover`：桌面 `width: 220px; aspect-ratio: 3/4; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl); border:1px solid var(--color-border-default); flex-shrink:0;`
- 資訊 `.info`：`flex:1; padding-bottom: 8px;`
  - 標題 `h1`：`var(--font-display)`、`--font-size-3xl`（桌面 32px）、700、`--line-height-tight`。
  - Meta 列：分類 tag（`--color-accent-soft` 底、`--color-accent` 字、`--radius-full`、padding 4px 12px、12px）+「`{episodeCount} 集`」（secondary），中間用 8px gap。
  - 簡介 `.desc`：`--color-text-secondary`、15px、`--line-height-relaxed`、max-width 65ch。
  - 上次進度 pill：`--color-success-soft` 底、success 字、`--radius-full`、padding 4px 12px、13px（「上次看到：第 N 集」）。
- **主 CTA（新增）**：「▶ 開始觀看」→ 若有 progress 就跳上次集數，否則跳第一集（`drama.episodes[0].id`）。樣式同 hero 主鈕，`--gradient-accent`、`--radius-full`、padding 13px 32px。
- 區段標題 `.sectionTitle`：「集數列表」20px、600、下方配一條 `--color-border-subtle` 分隔線（`padding-bottom: 12px; border-bottom: 1px solid var(--color-border-subtle);`）。
- **Responsive**：手機（<640px）header 改直向：cover 縮到 140px、資訊喺右側或下方；標題縮到 26px。

### 6.4 Play（`app/play/PlayClient.tsx`）

- 外層 `.playerWrap`：`max-width: 1000px; margin: 0 auto; padding-top: var(--spacing-4);`
- 影片 `<video>`：`width:100%; aspect-ratio:16/9; background:#000; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl); display:block;`
- 資訊區 `.info`：`padding: var(--spacing-4) var(--spacing-2);`
  - 標題：18px、600、primary。
  - 集名：14px、secondary。
  - 上／下一集 `.navBtn`：
    - `下一集` = filled `var(--gradient-accent)` 主鈕（鼓勵 binge）。
    - `上一集` = ghost outline 鈕。
    - 統一 `--radius-full`、padding 10px 22px、disabled 透明度 0.4。
- Loading：spinner（同 ProtectedRoute）置中；Error：error pill + 重試。

---

## 7. Loading / Empty / Error State

| State | 設計 |
|---|---|
| **Loading（grid）** | 取代「載入中…」文字為 **skeleton**：同 DramaCard 尺寸嘅灰塊（`--color-surface`），上面疊一層 moving shimmer（`@keyframes shimmer`，1.6s）。每個 skeleton 由封面灰塊（3:4）+ 下方兩條短灰條組成。 |
| **Loading（詳情／播放）** | 置中 spinner（見 §5.4）。 |
| **Empty** | 置中：一個 48px 虛線圓框 icon（`--color-border-default`）+「目前沒有劇集」（secondary）+ 細字「稍後再回來看看」（tertiary）。padding 60px 0。 |
| **Error** | error pill（`--color-error-soft` 底、error 字）+ 一個「重試」ghost 鈕（重新觸發當前 fetch，只需在頁面加一個 onClick 重跑既有 useEffect 邏輯，唔改 API）。 |

Shimmer keyframes：
```css
@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
.skeleton {
  background: linear-gradient(90deg, #1a1a22 0px, #23232e 40px, #1a1a22 80px);
  background-size: 800px 100%;
  animation: shimmer 1.6s linear infinite;
}
```

---

## 8. 實作建議（Gradient / Backdrop / 動畫）

- **用 CSS gradient 嘅位**：hero 背景壓暗、卡片底部 scrim、所有 primary 按鈕、登入卡表面、捲軸外圍紅光。
- **用 `backdrop-filter: blur()` 嘅位**：Navbar、卡片上嘅分類 chip、hover 播放鈕。只喺夠暗嘅半透明底上用；`backdrop-filter` 唔好濫用喺大面積，會耗效能。
- **圖片 hover**：對 `<img>` 做 `transform: scale()`，唔好對外層 card scale（避免文字一齊放大）。
- **過場統一**：
  - 快速（chip、border、opacity）：`var(--motion-fast)`（150ms）+ `ease-out`。
  - 一般（卡片浮起、按鈕）：`var(--motion-base)`（250ms）+ `ease-out`。
  - 圖片 zoom：`var(--motion-slow)`（400ms）+ `ease-out`。
  - 彈出（播放鈕出現）：`ease-spring`。
- **必做**：`prefers-reduced-motion` 關閉動畫（見 §4）；所有互動元素有 `:focus-visible`。
- **字串**：新字串一律繁中（立即觀看、開始觀看、查看詳情、重試、熱門、已觀看、載入中…）。

---

## 9. Web 逐檔改動清單

| 檔案 | 改動 |
|---|---|
| `app/globals.css` | 加入 `:root` tokens（§1）、更新 body/container/scrollbar/focus（§4） |
| `app/layout.tsx` | `<head>` 加 Noto Sans/Serif TC 字體 link；body 可加 `style` 或 class 掛背景 |
| `app/page.tsx` + `.module.css` | 加 hero（取 dramas[0]）、tabs 膠囊、grid、skeleton/empty/error |
| `app/login/page.module.css` | 卡片玻璃化、漸層按鈕、input focus ring、divider |
| `app/drama/DramaDetailClient.tsx` + `.module.css` | 大海報 + 資訊排版、主 CTA「開始觀看」、section 分隔線 |
| `app/play/PlayClient.tsx` + `.module.css` | 影片圓角陰影、下一集 filled 主鈕、spinner |
| `components/Navbar.*` | 玻璃 sticky、logo mark、按鈕膠囊化 |
| `components/DramaCard.*` | 海報式：scrim、分類 chip、底部標題、hover 播放鈕、placeholder 漸層 |
| `components/EpisodeList.*` | surface 卡片、current accent-soft、watched success |
| `components/ProtectedRoute.*` | spinner 置中 |

---

# 10. Android 對應（Jetpack Compose）

> Android project：`android/`（Kotlin + Compose + Material3 + Navigation + Retrofit + Coil + Media3）。
> 目標：**同一套色調、卡片質感、登入頁、詳情頁**落到手機端，行為同 web 對齊。
> 現狀問題：`Color.kt` 仲係 template 紫色 + `DramaAccent=#FF4D6D`／`DramaDark=#1A1A2E`；`Type.kt` 係預設 `Typography()`；Home 卡片分類只寫 `category?.name ?: "分類未設定"`（缺 fallback）；Login 淨係 OTP、無 Google SSO。

## 10.1 顏色對應（`ui/theme/Color.kt`）

刪走 template 紫色，改為以下，名稱與 web token 一一對應：

```kotlin
package com.drama.app.ui.theme

import androidx.compose.ui.graphics.Color

// 背景階層
val BgDeep        = Color(0xFF07070B)
val BgPrimary     = Color(0xFF0B0B10)
val BgSecondary   = Color(0xFF121219)
val Surface       = Color(0xFF16161E)
val SurfaceRaised  = Color(0xFF1E1E28)
val SurfaceSunken = Color(0xFF0E0E14)

// 邊框（Compose 用 alpha 疊白色）
val BorderSubtle  = Color(0x0FFFFFFF)  // white @ 6%
val BorderDefault = Color(0x1AFFFFFF)  // white @ 10%
val BorderStrong  = Color(0x2EFFFFFF) // white @ 18%

// 主 accent（暖紅）
val Accent        = Color(0xFFE63846)
val AccentHover   = Color(0xFFF04554)
val AccentPress   = Color(0xFFC42735)
val AccentSoft    = Color(0x24E63846) // accent @ 14%
val AccentGlow    = Color(0x59E63846) // accent @ 35%

// 琥珀金
val Gold     = Color(0xFFF5B942)
val GoldSoft = Color(0x29F5B942)

// 文字
val TextPrimary   = Color(0xFFF5F5F7)
val TextSecondary = Color(0xFFA6A6B2)
val TextTertiary  = Color(0xFF6E6E7A)
val TextDisabled  = Color(0xFF4A4A55)
val TextOnAccent  = Color(0xFFFFFFFF)

// 語意
val Success      = Color(0xFF3DD68C)
val SuccessSoft  = Color(0x243DD68C)
val ErrorC       = Color(0xFFFF5C6C)
val ErrorSoft    = Color(0x1FFF5C6C)
val Warning      = Color(0xFFFBBF24)
val Info         = Color(0xFF5EA8FF)
```

> 注意：Material3 預設 `error` 同 `primary` 都係紅色易撞色，要明確把 `error = ErrorC` 設入 colorScheme（見 10.4）。

## 10.2 Typography 對應（`ui/theme/Type.kt`）

取代空白 `Typography()`，用 Compose 對應 web 級距（字重／行高）：

```kotlin
package com.drama.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// 建議把 Noto Sans TC / Noto Serif TC 放進 res/font 後用 FontFamily，
// 此處先用系統 sans，display 用 serif fallback。
val DisplayFont = FontFamily.Serif   // 換成 NotoSerifTC 後改這裡
val SansFont    = FontFamily.Default

val DramaTypography = Typography(
    displayLarge  = TextStyle(fontFamily = DisplayFont, fontWeight = FontWeight.Bold, fontSize = 34.sp, lineHeight = 40.sp), // 詳情頁大標
    headlineMedium = TextStyle(fontFamily = DisplayFont, fontWeight = FontWeight.Bold, fontSize = 24.sp, lineHeight = 30.sp), // 登入「歡迎回來」
    titleLarge    = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 20.sp, lineHeight = 26.sp), // 區段標題
    titleMedium   = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 16.sp, lineHeight = 22.sp), // 影片標題 / 卡片標題
    titleSmall    = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 14.sp, lineHeight = 20.sp),
    bodyLarge     = TextStyle(fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 24.sp), // 輸入框
    bodyMedium    = TextStyle(fontWeight = FontWeight.Normal, fontSize = 14.sp, lineHeight = 22.sp), // 內文
    bodySmall     = TextStyle(fontWeight = FontWeight.Normal, fontSize = 13.sp, lineHeight = 18.sp),
    labelSmall    = TextStyle(fontWeight = FontWeight.Medium, fontSize = 11.sp, lineHeight = 14.sp), // chip / badge
)
```

## 10.3 Theme（`ui/theme/Theme.kt`）— 固定走深色

短劇 App 情境係睇片，**強制深色**，唔跟系統淺色：

```kotlin
private val DarkColors = darkColorScheme(
    primary       = Accent,
    onPrimary     = TextOnAccent,
    secondary     = Gold,
    background    = BgPrimary,
    onBackground  = TextPrimary,
    surface       = Surface,
    onSurface     = TextPrimary,
    surfaceVariant= SurfaceRaised,
    onSurfaceVariant = TextSecondary,
    error         = ErrorC,
    onError       = TextOnAccent,
)

@Composable
fun ShortDramaTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColors,
        typography = DramaTypography,
        content = content,
    )
}
```

`MainActivity` 入面 `ShortDramaTheme { ... }` 唔使再傳 darkTheme。

## 10.4 組件 Compose 實作建議

**(a) TopAppBar（對應 web Navbar）**
- 用 `TopAppBar`，`colors = TopAppBarDefaults.topAppBarColors(containerColor = BgPrimary.copy(alpha=0.85), scrolledContainerColor = BgPrimary, titleContentColor = TextPrimary)`。
- 標題「短劇平台」左邊加一個 24.dp、圓角 6.dp、`Brush.linearGradient(listOf(AccentHover, AccentPress))` 嘅小方塊（`Box` + `clip`）做 logo mark。
- 手機號用 `Text(it, style = bodySmall, color = TextSecondary)`。
- 登出維持 DropdownMenuItem，但文字色用 TextSecondary。

**(b) DramaCard（海報式，對應 §5.2）**
- 用 `Card`（`elevation = CardDefaults.cardElevation(defaultElevation = 0.dp, pressedElevation = 8.dp)`，`shape = RoundedCornerShape(10.dp)`，`colors = CardDefaults.cardColors(containerColor = Surface)`）。
- 內層 `Box` 包 `AsyncImage`（`aspectRatio(3/4)`、`ContentScale.Crop`）。
- 封面底部疊漸層：`Box Modifier.matchParentSize().background(Brush.verticalGradient(listOf(Color.Transparent, Color.Black.copy(alpha=0.88)), startY=...))`。
- 頂左分類膠囊：`Box.background(BgBlack.copy(alpha=0.5f), RoundedCornerShape(50)).padding(horizontal=10.dp, vertical=3.dp)` + `Text(categoryLabel, style=labelSmall, color=TextPrimary)`。
- 底部：`Text(title, maxLines=2, style=titleSmall, color=TextPrimary)` + 一列紅點 +「N 集」（`bodySmall, TextSecondary`）。
- 點擊涟漪用 `localIndication`；按壓時 `Card`  elevation 升到 8.dp（等同 web hover 浮起）。
- Grid：現有 `GridCells.Fixed(2)` 保留；列間距 12.dp，內容 padding 16.dp。

**(c) EpisodeList / EpisodeRow（對應 §5.3）**
- 詳情頁現有 `EpisodeRow` 改為：`Card(containerColor = Surface, shape = RoundedCornerShape(10.dp), border = BorderStroke(1.dp, BorderSubtle))`。
- 「第 N 集」用 `titleSmall, color = Accent`；集名 `bodyMedium, TextSecondary`；時長 `bodySmall, TextTertiary`。
- 目前播放集：`containerColor = AccentSoft`，左側 3.dp 紅色 side bar（`Modifier.drawBehind` 或 `Row` 開頭一個 `Box(width=3.dp, height=... , background=Accent)`）。
- 已看進度：`Text("已看 X 分", color = Success)`。

**(d) FilterChip（分類膠囊）**
- 選中：`colors = FilterChipDefaults.filterChipColors(containerColor = Accent, labelColor = TextOnAccent)`，加陰影 elevation 4.dp。
- 未選中：`containerColor = SurfaceRaised, labelColor = TextSecondary, border = BorderStroke(1.dp, BorderDefault)`。

**(e) 按鈕**
- Primary：`Button`，`colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent)`，外層 `Modifier.background(Brush.linearGradient(listOf(AccentHover, AccentPress)), RoundedCornerShape(10.dp))` 包起，等同 web `--gradient-accent`；elevation 用 `ButtonDefaults.buttonElevation(defaultElevation = 6.dp, pressedElevation = 2.dp)`。
- Ghost/outline：`OutlinedButton`，border = BorderDefault。

## 10.5 登入頁：新增 Google SSO 按鈕（對應 web `/auth/google/authorize`）

現狀 Android LoginScreen 只有電話 OTP，要加一條同 web 一致嘅 Google 登入流程。

**流程設計**：
1. 登入頁頂部加一個滿版白底「使用 Google 帳號登入」按鈕（同 web 視覺：白底、黑字、左邊 Google G icon、圓角 10.dp）。
2. 點擊後開啟 Chrome Custom Tab 載入：
   ```
   BuildConfig.API_BASE_URL + "/auth/google/authorize"
   ```
   （即對應 web 嘅 `${API_BASE_URL}/auth/google/authorize` 跳轉。）
3. 後端 OAuth 完成後會 redirect 回一個帶 fragment `#access_token=...&refresh_token=...` 的 URL。**需要後端配合加一個給 Android 的 redirect**（例如 deep link `dramaapp://oauth/callback`）。

**建議實作（Custom Tab + App Link）**：
- 加依賴：`implementation "androidx.browser:browser:1.8.0"`（Chrome Custom Tabs）。
- `AndroidManifest.xml` 為 `MainActivity` 加 intent-filter，接收 deep link（假設 redirect host 為 `oauth/callback`，scheme 用 `dramaapp`）：
  ```xml
  <intent-filter android:autoVerify="false">
      <action android:name="android.intent.action.VIEW" />
      <category android:name="android.intent.category.DEFAULT" />
      <category android:name="android.intent.category.BROWSABLE" />
      <data android:scheme="dramaapp" android:host="oauth" android:pathPrefix="/callback" />
  </intent-filter>
  ```
- 點擊 Google 鈕：`CustomTabsIntent.Builder().build().launchUrl(activity, Uri.parse("${BuildConfig.API_BASE_URL}/auth/google/authorize?redirect_uri=dramaapp://oauth/callback"))`（redirect_uri 參數名以後端實際為準；web 端係固定 redirect 到 SPA，Android 要後端加白名單）。
- `MainActivity.onCreate`／`onNewIntent` 攔截 `intent.data`：解析 URL **fragment**（`uri.fragment`）取出 `access_token`、`refresh_token`（同 web `window.location.hash` 做法一致），存入 `TokenManager`，再用 `Authorization: Bearer <accessToken>` 打 `GET auth/me` 取得 user，完成後導去 `HOME`。

**若後端暫時唔加 deep link redirect（fallback）**：
- 改用 app 內 `WebView` 載入 `/auth/google/authorize`，`WebViewClient.shouldOverrideUrlLoading` 偵測 URL 出現 `#access_token=` 時攔截、解析 fragment、關 WebView、走上面同樣的存 token 流程。優點係唔使後端改 redirect；缺點係要用 WebView。**建議優先 Custom Tab，WebView 僅作過渡方案。**

**Repo 層補充**：`AuthRepository` 加
```kotlin
suspend fun saveGoogleTokens(accessToken: String, refreshToken: String): Boolean {
    tokenManager.saveTokens(accessToken, refreshToken)
    return true
}
```
（攞 user 可重用現有 `me()`。）

## 10.6 分類名顯示修正（同 web 一致）

web 用 `drama.category?.name ?? drama.categoryName ?? '未分類'`。Android 而家：
- `HomeScreen.DramaCard`：`drama.category?.name ?: "分類未設定"` ❌
- `DramaDetailScreen`：`d.category?.name ?: "未分類"` ❌（缺 `categoryName` fallback）

**修正**：
1. `data/model/Drama.kt` 的 `Drama` 與 `DramaDetail` 加回退欄位（對應 web flat field）：
   ```kotlin
   @SerialName("category_name") val categoryName: String? = null,
   ```
2. 加一個 extension 統一顯示：
   ```kotlin
   val Drama.categoryLabel: String
       get() = category?.name ?: categoryName ?: "未分類"
   ```
   （`DramaDetail` 繼承或同樣提供。）
3. Home 卡片、詳情頁 meta 全部改用 `drama.categoryLabel`，唔好再 hardcode「分類未設定」。

## 10.7 Android 逐檔改動清單

| 檔案 | 改動 |
|---|---|
| `ui/theme/Color.kt` | 刪紫色，換 §10.1 全部色 |
| `ui/theme/Type.kt` | 換 §10.2 DramaTypography |
| `ui/theme/Theme.kt` | 固定深色 darkColorScheme（§10.3） |
| `ui/home/HomeScreen.kt` | TopAppBar 加 logo mark；DramaCard 海報式（scrim＋分類膠囊＋2 行標題）；分類用 `categoryLabel` |
| `ui/login/LoginScreen.kt` | 頂部加 Google SSO 鈕 → Custom Tab；其餘 OTP 樣式對齊 web（漸層主鈕、focus 色） |
| `ui/detail/DramaDetailScreen.kt` | 封面 hero、標題用 display、分類 `categoryLabel`、EpisodeRow 用 accent/soft 色 |
| `data/model/Drama.kt` | 加 `categoryName` 欄位 + `categoryLabel` extension |
| `data/repository/AuthRepository.kt` | 加 `saveGoogleTokens` |
| `MainActivity.kt` | 攔截 deep link / WebView callback，解析 fragment 存 token |
| `AndroidManifest.xml` | 加 Google SSO callback intent-filter |
| `app/build.gradle.kts` | 加 `androidx.browser:browser`（Custom Tab） |

---

## 11. 验收標準（DoD）

- [ ] 任何畫面唔再出現寫死嘅 `#141418 / #e53945 / #22222a`，全部走 tokens。
- [ ] DramaCard 海報壓暗、標題可读、hover 浮起＋圖片放大。
- [ ] Navbar 玻璃模糊、CTA 紅漸層。
- [ ] Login 卡有質感、Google 鈕＋OTP 兩條流程都正常。
- [ ] 分類名永遠 `category?.name ?? categoryName ?? '未分類'`。
- [ ] Loading 係 skeleton／spinner，唔再係乾脆一行灰字。
- [ ] Android 色／字體同 web token 對齊；Login 有 Google SSO；分類 fallback 修正。
