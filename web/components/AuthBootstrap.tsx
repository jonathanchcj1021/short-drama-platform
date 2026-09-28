'use client';

import { useEffect } from 'react';
import { bootstrapSession } from '@/lib/apiClient';

/**
 * App 啟動時主動驗證 / 刷新一次 session，避免 access token 過期時 UI 閃一下。
 * 本身唔渲染任何嘢，純副作用。
 */
export default function AuthBootstrap() {
  useEffect(() => {
    void bootstrapSession();
  }, []);
  return null;
}
