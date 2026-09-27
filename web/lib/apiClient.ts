import { getAccessToken, clearAuth } from './auth';
import type { ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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

/** 統一 fetch 包裝：自動帶 Authorization、處理 401 跳轉登入 */
export async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
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
      // 靜態 SPA 不共用 Cookie，一律帶 token
      credentials: 'omit',
    });
  } catch (e) {
    const err: ApiError = { message: '網路連線失敗，請稍後再試', status: 0 };
    throw err;
  }

  // 401：清除憑證並跳轉登入頁
  if (res.status === 401) {
    clearAuth();
    if (typeof window !== 'undefined') {
      const loginUrl = '/login';
      // basePath 在 production 由 Next 處理，這裡直接導回首頁登入
      window.location.href = loginUrl;
    }
    const err: ApiError = { message: '登入已失效，請重新登入', status: 401 };
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
