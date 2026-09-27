'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, API_BASE_URL } from '@/lib/apiClient';
import { saveAuth } from '@/lib/auth';
import type { OtpRequestResponse, OtpVerifyResponse, User } from '@/types';
import styles from './page.module.css';

const COOLDOWN_SEC = 60;

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden>
      <path
        fill="#4285F4"
        d="M17.64 9.2c0-.63-.06-1.23-.16-1.82H9v3.45h4.84a4.13 4.13 0 0 1-1.8 2.71v2.26h2.92c1.71-1.58 2.68-3.9 2.68-6.6z"
      />
      <path
        fill="#34A853"
        d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"
      />
      <path
        fill="#FBBC05"
        d="M3.97 10.72a5.4 5.4 0 0 1 0-3.44V4.95H.96a9 9 0 0 0 0 8.1l3.01-2.33z"
      />
      <path
        fill="#EA4335"
        d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"
      />
    </svg>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Google SSO 回調：token 喺 URL fragment（#access_token=...&refresh_token=...）
  useEffect(() => {
    const hash = window.location.hash;
    if (hash.includes('access_token=')) {
      const params = new URLSearchParams(hash.slice(1));
      const accessToken = params.get('access_token') ?? '';
      const refreshToken = params.get('refresh_token') ?? '';
      if (accessToken && refreshToken) {
        setBusy(true);
        fetch(`${API_BASE_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
          credentials: 'omit',
        })
          .then((res) => {
            if (!res.ok) throw new Error('取得使用者資料失敗');
            return res.json() as Promise<User>;
          })
          .then((user) => {
            saveAuth(accessToken, refreshToken, user);
            router.replace('/');
          })
          .catch((e: { message?: string }) => {
            setBusy(false);
            setError(e.message ?? 'Google 登入失敗，請重試');
          });
      }
    }

    const q = new URLSearchParams(window.location.search);
    const err = q.get('error');
    if (err) setError(err);
  }, [router]);

  // 倒數計時
  useEffect(() => {
    if (countdown <= 0) return;
    const t = setTimeout(() => setCountdown((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const handleGoogleLogin = () => {
    setError(null);
    setBusy(true);
    window.location.href = `${API_BASE_URL}/auth/google/authorize`;
  };

  const handleSendOtp = async () => {
    setError(null);
    if (!/^\+?[0-9]{8,15}$/.test(phone.trim())) {
      setError('請輸入正確的手機號碼（可加國碼，如 +852）');
      return;
    }
    setBusy(true);
    try {
      await apiClient<OtpRequestResponse>('/auth/otp/request', {
        method: 'POST',
        auth: false,
        body: { phone_number: phone.trim() },
      });
      setOtpSent(true);
      setCountdown(COOLDOWN_SEC);
    } catch (e: unknown) {
      setError((e as { message?: string }).message ?? '發送失敗');
    } finally {
      setBusy(false);
    }
  };

  const handleVerify = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!/^\d{6}$/.test(otp.trim())) {
      setError('請輸入 6 位數驗證碼');
      return;
    }
    setBusy(true);
    try {
      const data = await apiClient<OtpVerifyResponse>('/auth/otp/verify', {
        method: 'POST',
        auth: false,
        body: { phone_number: phone.trim(), code: otp.trim() },
      });
      saveAuth(data.access_token, data.refresh_token, data.user);
      router.push('/');
    } catch (err: unknown) {
      setError((err as { message?: string }).message ?? '驗證失敗');
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className={styles.wrap}>
      <div className={styles.card}>
        <h1 className={styles.title}>歡迎回來</h1>
        <p className={styles.subtitle}>電話驗證碼 或 Google 登入</p>

        {error && <p className={styles.error}>{error}</p>}

        <button
          type="button"
          className={styles.googleBtn}
          onClick={handleGoogleLogin}
          disabled={busy}
        >
          <GoogleIcon />
          {busy ? '處理中…' : '使用 Google 帳號登入'}
        </button>

        <div className={styles.divider}>
          <span className={styles.dividerLine} />
          <span className={styles.dividerText}>或用手機號碼</span>
          <span className={styles.dividerLine} />
        </div>

        <form onSubmit={handleVerify} className={styles.form}>
          <label className={styles.field}>
            <span>手機號碼</span>
            <input
              type="tel"
              inputMode="tel"
              placeholder="請輸入手機號碼"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/[^\d+]/g, ''))}
              maxLength={16}
              disabled={otpSent}
              className={styles.input}
            />
          </label>

          {!otpSent ? (
            <button
              type="button"
              className={styles.primaryBtn}
              onClick={handleSendOtp}
              disabled={busy || countdown > 0}
            >
              {countdown > 0 ? `${countdown}s 後重發` : '發送驗證碼'}
            </button>
          ) : (
            <>
              <label className={styles.field}>
                <span>驗證碼</span>
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="請輸入 6 位驗證碼"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  maxLength={6}
                  className={styles.input}
                />
              </label>

              <button type="submit" className={styles.primaryBtn} disabled={busy}>
                {busy ? '驗證中…' : '驗證登入'}
              </button>

              <button
                type="button"
                className={styles.ghostBtn}
                onClick={handleSendOtp}
                disabled={busy || countdown > 0}
              >
                {countdown > 0 ? `${countdown}s 後可重發` : '重新發送驗證碼'}
              </button>
            </>
          )}
        </form>
      </div>
    </main>
  );
}
