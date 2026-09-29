import type { User } from '@/types';

// localStorage key
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

/** 讀取 access token */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

/** 讀取 refresh token */
export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

/** 讀取目前使用者 */
export function getUser(): User | null {
  if (typeof window === 'undefined') return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

/** 是否已登入（有 access token） */
export function isLoggedIn(): boolean {
  return Boolean(getAccessToken());
}

/** 儲存登入憑證 */
export function saveAuth(accessToken: string, refreshToken: string, user: User): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/** 只更新 access / refresh token（不動 user）；用於 refresh token 換新時 */
export function saveTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

/** 只更新本機快取嘅使用者資料（唔動 token） */
export function saveUser(user: User): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/** 登出：清除本機憑證 */
export function clearAuth(): void {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

/**
 * 判斷用家是否有效 VIP。
 * 條件：membership_tier 唔係 free、有 vip_expires_at、而且到期日未過。
 * 純前端計算，唔依賴後端 is_vip flag（避免 clock skew ／ 本機舊資料唔一致）。
 */
export function isVip(user: User | null): boolean {
  if (!user) return false;
  if (!user.membership_tier || user.membership_tier === 'free') return false;
  if (!user.vip_expires_at) return false;
  const exp = new Date(user.vip_expires_at);
  if (Number.isNaN(exp.getTime())) return false;
  return exp.getTime() > Date.now();
}

/** 格式化 VIP 到期日做 YYYY-MM-DD（local timezone）；無效回傳空字串 */
export function formatVipExpiry(user: User | null): string {
  if (!user?.vip_expires_at) return '';
  const d = new Date(user.vip_expires_at);
  if (Number.isNaN(d.getTime())) return '';
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
