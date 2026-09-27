import DramaDetailClient from './DramaDetailClient';

// 靜態匯出（output: export）：/drama/ 為靜態頁面，
// 實際劇集 id 由 DramaDetailClient 讀取查詢參數 ?id=（客戶端 fetch），
// 因此 CMS 新增劇集無需重新 build。
export default function Page() {
  return <DramaDetailClient />;
}
