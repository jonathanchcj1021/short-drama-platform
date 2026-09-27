import PlayClient from './PlayClient';

// 靜態匯出（output: export）：/play/ 為靜態頁面，
// 實際集數 id 由 PlayClient 讀取查詢參數 ?episode=（客戶端 fetch）。
export default function Page() {
  return <PlayClient />;
}
