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
}

/** 劇集詳情（含集數列表） */
export interface DramaDetail extends Drama {
  episodes: Episode[];
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
