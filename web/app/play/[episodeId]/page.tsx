import PlayClient from './PlayClient';

// 靜態匯出（output: export）規定動態路由必須提供 generateStaticParams。
// 本頁所有資料皆由用戶端（PlayClient）以 fetch 取得，
// 這裡回傳一個 placeholder：build 時僅預渲染 /play/placeholder 作為樣板，
// 實際的 /play/[episodeId] 路由參數由用戶端 useParams() 讀取。
export function generateStaticParams() {
  return [{ episodeId: 'placeholder' }];
}

export default function Page() {
  return <PlayClient />;
}
