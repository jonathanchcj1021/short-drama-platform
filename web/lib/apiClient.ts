import { getAccessToken, getRefreshToken, saveAuth, saveUser, saveTokens, clearAuth } from './auth';
import type { ApiError, User } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
// GitHub Pages 專案頁 basePath（與 next.config.js 一致）；dev 下係空字串
const SITE_BASE_PATH = process.env.NODE_ENV === 'production' ? '/short-drama-platform' : '';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  /** 是否自動帶上 Authorization header（預設 true） */
  auth?: boolean;
  /** query 參數 */
  query?: Record<string, string | number | undefined>;
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = new URL(path, BASE_URL);
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== '') url.searchParams.set(k, String(v));
    });
  }
  return url.toString();
}

/** refresh 結果：用嚟分清楚「refresh token 真係唔 valid」定「網絡短暫唔得」 */
type RefreshResult = 'success' | 'invalid' | 'transient';

/**
 * 嘗試用 refresh token 攞新 access token。
 * - 'success'：換到新 token
 * - 'invalid'：服務器明確答 401/403（refresh token 真係過期／無效）→ 可以安全清 credential
 * - 'transient'：網絡錯誤／5xx／超時 → 唔好清 credential，等下次再試
 */
async function tryRefreshToken(): Promise<RefreshResult> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return 'invalid';
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: 'no-store',
    });
  } catch {
    return 'transient'; // 網絡／tunnel 慢：唔好亂清登入狀態
  }
  if (res.status === 401 || res.status === 403) return 'invalid';
  if (!res.ok) return 'transient'; // 5xx 等短暫故障
  const data = await res.json();
  // 只更新 token；若本機已有 user 就一併保留，冇就唔好寫入 "null" 字串蓋掉
  const userRaw = window.localStorage.getItem('user');
  if (userRaw) {
    saveAuth(data.access_token, refreshToken, JSON.parse(userRaw));
  } else {
    saveTokens(data.access_token, refreshToken);
  }
  return 'success';
}

/** 統一 fetch 包裝：自動帶 Authorization、401 時先嘗試 refresh，再失敗先跳登入 */
export async function apiClient<T>(path: string, options: RequestOptions = {}, _retried = false): Promise<T> {
  const { method = 'GET', body, auth = true, query } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (auth) {
    const token = getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      credentials: 'omit',
      cache: 'no-store',
    });
  } catch (e) {
    const err: ApiError = { message: '網路連線失敗，請稍後再試', status: 0 };
    throw err;
  }

  // 401：先嘗試 refresh token，成功就重試原 request
  if (res.status === 401 && auth && !_retried) {
    const result = await tryRefreshToken();
    if (result === 'success') {
      return apiClient<T>(path, options, true);
    }
    if (result === 'invalid') {
      // refresh token 真係唔 valid：清 credential 跳登入
      clearAuth();
      if (typeof window !== 'undefined') {
        window.location.href = `${SITE_BASE_PATH}/login`;
      }
      const err: ApiError = { message: '登入已失效，請重新登入', status: 401 };
      throw err;
    }
    // transient：網絡／tunnel 唔穩定，唔好清 credential、唔好跳 login，直接拋網絡錯誤
    const err: ApiError = { message: '網路連線不穩定，請稍後再試', status: 0 };
    throw err;
  }

  if (!res.ok) {
    let message = `請求失敗（${res.status}）`;
    try {
      const data = await res.json();
      if (data && typeof data.message === 'string') message = data.message;
      else if (data && typeof data.detail === 'string') message = data.detail;
    } catch {
      // ignore parse error
    }
    const err: ApiError = { message, status: res.status };
    throw err;
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  try {
    return (await res.json()) as T;
  } catch {
    return undefined as T;
  }
}

export { BASE_URL };
export const API_BASE_URL = BASE_URL;

/** bootstrap 完成嘅 Promise（全 App 只跑一次）；畀 ProtectedRoute 等佢完成先落決定 */
let bootstrapPromise: Promise<void> | null = null;

/**
 * 應用啟動時主動驗證一次 session（client-side bootstrapping）：
 * - 冇 token 就唔做任何嘢；
 * - 有 access token 就打 /auth/me，200 即有效，並順手更新本機 user；
 * - /auth/me 返 401 就用 refresh token 換新 access token；
 * - refresh 都失敗就清除憑證（各頁面自己會跳 /login）。
 * 咁樣 reload 之後唔會出現「access token 過期 → UI 閃一下先走」嘅狀況。
 */
async function runBootstrap(): Promise<void> {
  if (typeof window === 'undefined') return;
  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();
  if (!accessToken && !refreshToken) return;

  // 有 access token：先試 /auth/me
  if (accessToken) {
    try {
      const res = await fetch(`${BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        credentials: 'omit',
        cache: 'no-store',
      });
      if (res.ok) {
        const user = (await res.json()) as User;
        saveUser(user);
        return;
      }
      if (res.status !== 401) return; // 5xx 等：唔好亂清，交畀之後嘅 request
    } catch {
      return; // 網絡問題：唔好亂清
    }
  }

  // access token 無效 / 冇：嘗試用 refresh token 換新
  const result = await tryRefreshToken();
  // 只有服務器明確答 refresh token 無效（invalid）先清 credential；
  // 網絡短暫唔得（transient）就保留，等下次 request 再試，唔好趕客落登入頁。
  if (result === 'invalid') {
    clearAuth();
  }
}

/**
 * App 啟動入口：session bootstrap 只跑一次。
 * 完成（不論成功 / refresh 失敗清除憑證）後 broadcast `auth-changed`，
 * 等 Navbar 重新讀 localStorage 更新 UI state。
 */
export function bootstrapSession(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve();
  if (!bootstrapPromise) {
    bootstrapPromise = runBootstrap().finally(() => {
      window.dispatchEvent(new Event('auth-changed'));
    });
  }
  return bootstrapPromise;
}

/** 等 bootstrap 完成（未開始就即時 resolve）。畀 ProtectedRoute 用，避免 async 未完就誤跳 /login。 */
export function waitForBootstrap(): Promise<void> {
  return bootstrapPromise ?? Promise.resolve();
}
