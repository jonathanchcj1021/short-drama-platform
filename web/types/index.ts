// 全域共用型別定義

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
  coverUrl: string;
  categoryId: number;
  categoryName?: string;
  episodeCount: number;
  createdAt?: string;
}

/** 單集 */
export interface Episode {
  id: number;
  dramaId: number;
  episodeNumber: number;
  title: string;
  durationSec: number;
  videoUrl?: string;
}

/** 劇集詳情（含集數列表） */
export interface DramaDetail extends Drama {
  episodes: Episode[];
}

/** 觀看進度 */
export interface Progress {
  episodeId: number;
  positionSec: number;
  durationSec: number;
  updatedAt?: string;
}

/** 使用者 */
export interface User {
  id: number;
  phone?: string;
  phone_number?: string;
  email?: string;
  nickname?: string;
}

/** OTP 要求回應 */
export interface OtpRequestResponse {
  success: boolean;
  message?: string;
  expiresInSec?: number;
}

/** OTP 驗證回應 */
export interface OtpVerifyResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

/** API 錯誤結構 */
export interface ApiError {
  message: string;
  status: number;
}
