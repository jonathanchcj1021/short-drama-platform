// 全域共用型別定義
// 注意：FastAPI 後端回傳 snake_case JSON，此處型別直接對應 API 欄位，
// 經 apiClient<T>() 直接 res.json() as T，無需另外轉換。

/** 分類 */
export interface Category {
  id: number;
  name: string;
  slug?: string;
}

/** 劇集（短劇） */
export interface Drama {
  id: number;
  title: string;
  description: string;
  cover_url: string;
  category_id: number;
  category_name?: string;
  category?: { id?: number; name?: string } | null;
  /** 集數；後端尚未提供時為 null，此時不顯示 badge */
  episode_count: number | null;
  release_year?: number | null;
  is_completed?: boolean;
  /** 來源平台代碼（"hongguo" = 紅果短劇）；後端舊資料可能缺省 */
  source?: string | null;
  /** false = 呢套劇免費任睇，唔使睇廣告；預設（缺省 / true）係收費劇 */
  is_paid?: boolean;
  created_at?: string;
}

/** 單集 */
export interface Episode {
  id: number;
  drama_id: number;
  episode_number: number;
  title: string;
  video_url?: string;
  /** 時長（秒） */
  duration?: number | null;
  description?: string | null;
  /** 片種：缺省/null = 直片 mp4（<video>）；'youtube' = YouTube 官方 iframe */
  video_type?: string | null;
}

/** 廣告影片（CMS 上傳） */
export interface Ad {
  id: number;
  title: string;
  video_url: string;
  /** 時長（秒） */
  duration: number;
  /** 是否啟用 */
  active: boolean;
  created_at?: string;
}

/** 劇集詳情（含集數列表） */
export interface DramaDetail extends Drama {
  episodes: Episode[];
}

/** 劇集列表項（list endpoint 回傳，多咗 DB 真實集數） */
export interface DramaListItem extends Drama {
  /** DB 真實集數：優酷劇為 0（淨係 metadata），紅果劇有真集數 */
  real_episode_count: number;
}

/** GET /dramas 分頁回傳 envelope */
export interface DramaListPage {
  items: DramaListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/** 觀看進度 */
export interface Progress {
  episode_id: number;
  position_sec: number;
  duration_sec: number;
  updated_at?: string;
}

/** 使用者 */
export interface User {
  id: number;
  phone?: string;
  phone_number?: string;
  email?: string;
  nickname?: string;
  is_admin?: boolean;
  /** 會員等級：free = 免費；vip_monthly / vip_yearly = 有效 VIP（後端可能舊用戶未帶此欄位） */
  membership_tier?: 'free' | 'vip_monthly' | 'vip_yearly';
  /** VIP 到期日 ISO 字串；free 用戶為 null */
  vip_expires_at?: string | null;
  /** 後端算好嘅有效 VIP flag（與 vip_expires_at 一致，前端以 isVip() 為準） */
  is_vip?: boolean;
}

/** 訂閱方案 */
export type BillingPlan = 'monthly' | 'yearly';

/** GET /billing/me 回應 */
export interface BillingStatus {
  membership_tier: 'free' | 'vip_monthly' | 'vip_yearly';
  vip_expires_at: string | null;
  is_vip: boolean;
  monthly_price_hkd: number;
  yearly_price_hkd: number;
}

/** OTP 要求回應 */
export interface OtpRequestResponse {
  success: boolean;
  message?: string;
  expires_in_sec?: number;
}

/** OTP 驗證回應 */
export interface OtpVerifyResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

/** 登入回應（帳號密碼 / OTP / Google 通用） */
export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  user: User;
}

/** API 錯誤結構 */
export interface ApiError {
  message: string;
  status: number;
}
