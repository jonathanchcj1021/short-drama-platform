# 短劇平台 Android 客戶端

短劇平台 monorepo 的 Android App（Kotlin + Jetpack Compose + Media3/ExoPlayer）。
這是 MVP 版本，包含登入、劇集列表、劇集詳情、影片播放四個頁面。

> 本目錄僅含 Android 客戶端；後端在 `../backend/`，Web 前台在 `../web/`。

---

## 1. 先決條件

- **Android Studio Hedgehog (2023.1.1) 或更新**（推薦 Iguana / Jelly Fish）
- **JDK 17**（Android Studio 內建的 JBR 即可，無需另外安裝）
- **Android SDK 34（Android 14）** + 最新 Build-Tools（Android Studio 開啟後會自動下載）
- 本機已可執行後端（Python 3.11+、uvicorn）

| 項目 | 版本 |
|---|---|
| compileSdk / targetSdk | 34 |
| minSdk | 26（Android 8.0） |
| Gradle Wrapper | 8.5 |
| Android Gradle Plugin (AGP) | 8.2.2 |
| Kotlin | 1.9.22 |
| Compose BOM | 2024.02.00 |
| Media3 | 1.2.1 |

---

## 2. 用 Android Studio 開啟本專案

1. 開啟 Android Studio。
2. 選 **File → Open**。
3. 選擇 **`android/` 這個目錄**（不是 monorepo 根目錄，也不是 `app/`），按下 Open。
4. 等待第一次 Gradle Sync：Android Studio 會自動用專案內嘅 **Gradle Wrapper**（`./gradlew`，版本 8.5），唔需要另外安裝 Gradle。
   - 若出現「Gradle JDK」設定，請選 **JDK 17**（通常是 Android Studio 內建的 jbr-17）。
5. Sync 成功後即可建置。

> 第一次同步會花較久（需下載依賴），屬正常現象。
>
> 💡 **唔想開 Android Studio？** 可以直接用命令列 `./gradlew` 建置同安裝，詳見下方[第 10 節](#10-本機命令列建置與執行)。

---

## 3. 建立並啟動 Android Emulator

1. Android Studio 右上點 **Device Manager**（或 View → Tool Windows → Device Manager）。
2. 點 **Create Virtual Device**。
3. 選手機：**Pixel 6**（或任意 Pixel），Next。
4. 系統映像選 **API 34（Android 14，Google Play 或 ATD 皆可）**，下載後選它，完成。
5. 在 Device Manager 按下 ▶ 啟動該 Emulator。
6. 確認後端正在本機跑（見下一段），再按 Android Studio 工具列的 ▶ Run 'app'，選剛剛的 Emulator。

---

## 4. 啟動後端

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- 後端跑在 `http://127.0.0.1:8000`。
- 注意 `--host 0.0.0.0`：雖然 Emulator 走 `10.0.2.2`，但這樣設定可同時支援實體機/區網連線。
- 健康檢查：瀏覽器開 `http://127.0.0.1:8000/health` 應回 `{"status":"ok"}`。

---

## 5. App 如何連到後端

Android Emulator 有個特殊網路位址：

- Emulator 內的 `10.0.2.2` = **主機電腦的 `127.0.0.1`**。

因此 App 預設的 `BuildConfig.API_BASE_URL` 已設為：

```
http://10.0.2.2:8000
```

無需任何設定即可在 Emulator 內連到本機後端。此值定義在 `app/build.gradle.kts`。

開發期已於 `AndroidManifest.xml` 開啟 `android:usesCleartextTraffic="true"`，並設定
`res/xml/network_security_config.xml` 允許 `10.0.2.2` / `127.0.0.1` 的明文 HTTP。

---

## 6. 如何覆寫 API base URL

如果要連到區網內另一隻手機實體機，或後端跑在別的位置：

1. 在 `android/` 目錄建立 `local.properties`（已被 `.gitignore` 忽略）。
2. 加入一行：

   ```properties
   api.base.url=http://你的電腦IP:8000
   ```

   例如：

   ```properties
   api.base.url=http://192.168.1.10:8000
   ```

3. 重新 Sync / Run。`app/build.gradle.kts` 會讀這個 key 並覆寫 `BuildConfig.API_BASE_URL`。
   （範例見 `local.properties.example`）

> 用實體手機測試時，手機和電腦必須在同一個 Wi-Fi，且後端用 `--host 0.0.0.0` 啟動。

---

## 7. Mock OTP 登入流程

後端是開發版，**不會真的發簡訊**，驗證碼直接印在後端 log：

1. 開 App → 進入登入頁。
2. 輸入任意符合規則的手機號碼（例如 `0912345678`），按「發送驗證碼」。
3. 到**執行 uvicorn 的終端機**看 log，會出現類似：

   ```
   INFO: OTP for 0912345678: 482913
   ```

4. 把那 6 位數輸入 App，按「驗證登入」。
5. 成功後 token 存入本機，自動跳回首頁。

（60 秒倒數冷卻由前端控制；重發需等倒數結束。）

---

## 8. 功能與頁面

| 頁面 | 路由 | 說明 |
|---|---|---|
| 登入 | `login` | 手機號 + OTP，含 60 秒倒數 |
| 首頁 | `home` | 分類 Chip 篩選 + 2 欄劇集網格（Coil 載封面） |
| 詳情 | `detail/{dramaId}` | 大圖、介紹、集數清單、觀看進度 |
| 播放 | `play/{episodeId}/{dramaId}` | ExoPlayer 16:9、每 10 秒回報進度、上下集切換 |

網路層：Retrofit + OkHttp，Interceptor 自動帶 `Authorization: Bearer <token>`；
收到 **401** 時清除 token 並自動導回登入頁。DI 為手動 `AppContainer`（未用 Hilt）。

---

## 9. 已知限制（MVP）

- 開發期 `usesCleartextTraffic="true"`，正式版需關閉並改用 HTTPS。
- 僅 MVP：無註冊流程、無搜尋頁、無分頁載入（一次抓 20 筆）、無斷線重試。
- 影片為靜態 mp4 佔位，無轉碼 / CDN / HLS，ExoPlayer 直接抓 `video_url`。
- 未做 Release 混淆 / 簽章設定；icon 為向量預設圖。
- 後端 `/dramas` 目前回傳純陣列（非分頁包裝），App 已對應；未來後端若改分頁格式可再擴充。

---

## 10. 本機命令列建置與執行

專案已包含 **Gradle Wrapper**（`gradlew`、`gradlew.bat`、`gradle/wrapper/`），唔需要另外安裝 Gradle。
所有命令喺 `android/` 目錄下執行。

### 10.1 先決條件（命令列建置）

- **JDK 17**（命令列 `java -version` 確認；macOS 可用 `brew install openjdk@17`）
- **Android SDK**（裝咗 Android Studio 就有，通常喺 `~/Library/Android/sdk`）

### 10.2 設定 Android SDK 路徑

命令列建置需要話畀 Gradle 聽 SDK 喺邊，有兩種方法（揀其一）：

**方法 A：`local.properties`（推薦，Android Studio 都會自動寫）**

喺 `android/` 目錄建立 `local.properties`：

```properties
sdk.dir=/Users/你的用戶名/Library/Android/sdk
# 可選：覆寫 API base URL
# api.base.url=http://10.0.2.2:8000
```

> 用 Android Studio 開過一次專案後，`local.properties` 會自動生成，唔使手動加。

**方法 B：環境變數**

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

可以加落 `~/.zshrc` 永久生效。

### 10.3 建置 APK

```bash
cd android
./gradlew assembleDebug
```

成功後 APK 喺：
```
app/build/outputs/apk/debug/app-debug.apk
```

### 10.4 安裝到 Emulator / 實機

先確認有裝置連線（Emulator 已啟動或 USB 連接實機）：

```bash
# 查看已連線裝置
adb devices

# 安裝並自動開啟 App
./gradlew installDebug
```

`installDebug` 會自動安裝到第一個已連線嘅裝置。如果有多個裝置，用 `adb -s <裝置ID> install app/build/outputs/apk/debug/app-debug.apk`。

### 10.5 其他常用命令

```bash
./gradlew tasks              # 列出所有可用 task
./gradlew clean              # 清理 build 目錄
./gradlew lintDebug          # 跑 Lint 檢查
./gradlew assembleRelease    # 建置 Release APK（需要簽章設定）
```

### 10.6 macOS 常見問題

| 問題 | 解決方法 |
|---|---|
| `./gradlew: Permission denied` | `chmod +x gradlew` |
| `SDK location not found` | 設定 `local.properties` 嘅 `sdk.dir` 或 `ANDROID_HOME` |
| `Unsupported class file major version` | 確認用緊 JDK 17（`java -version`），AGP 8.2 要求 JDK 17 |
| Build 好慢 | 首次需下載 Gradle 8.5 同所有依賴，之後有快取 |
