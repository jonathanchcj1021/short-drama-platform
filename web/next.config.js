/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  // 靜態匯出：輸出 out/ 目錄，部署到 GitHub Pages
  output: 'export',
  // GitHub Pages 專案頁網址為 https://<user>.github.io/short-drama-platform/
  basePath: isProd ? '/short-drama-platform' : '',
  assetPrefix: isProd ? '/short-drama-platform' : undefined,
  // 靜態匯出不支援 Next.js 圖片最佳化，關閉之
  images: {
    unoptimized: true,
  },
  // 靜態匯出期間略過 ESLint，避免阻塞 build
  eslint: {
    ignoreDuringBuilds: true,
  },
  // 靜態匯出不支援伺服器動態參數，統一由用戶端讀取
  trailingSlash: true,
};

module.exports = nextConfig;
