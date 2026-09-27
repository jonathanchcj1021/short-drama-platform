import DramaDetailClient from './DramaDetailClient';

// 靜態匯出（output: export）規定動態路由必須提供 generateStaticParams。
// 本頁所有資料皆由用戶端（DramaDetailClient）以 fetch 取得，
// 這裡回傳一個 placeholder：build 時僅預渲染 /drama/placeholder 作為樣板，
// 實際的 /drama/[id] 路由參數由用戶端 useParams() 讀取。
export function generateStaticParams() {
  return [{ id: 'placeholder' }];
}

export default function Page() {
  return <DramaDetailClient />;
}
