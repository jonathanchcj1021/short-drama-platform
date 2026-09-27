'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, API_BASE_URL } from '@/lib/apiClient';
import { saveAuth } from '@/lib/auth';
import type { OtpRequestResponse, OtpVerifyResponse, TokenPair, User } from '@/types';
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

type Mode = 'login' | 'register';

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>('login');

  // 登入表單
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');

  // 註冊表單
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirm, setRegConfirm] = useState('');
  const [regNickname, setRegNickname] = useState('');

  // OTP 登入（備用，預設收起）
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [showOtp, setShowOtp] = useState(false);

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

  // ---------- 帳號密碼登入 ----------
  const handlePasswordLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!identifier.trim() || !password) {
      setError('請輸入帳號（手機號碼或 email）同密碼');
      return;
    }
    setBusy(true);
    try {
      const data = await apiClient<TokenPair>('/auth/login', {
        method: 'POST',
        auth: false,
        body: { identifier: identifier.trim(), password },
      });
      saveAuth(data.access_token, data.refresh_token, data.user);
      router.push('/');
    } catch (err: unknown) {
      setError((err as { message?: string }).message ?? '登入失敗');
    } finally {
      setBusy(false);
    }
  };

  // ---------- 公開註冊 ----------
  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const email = regEmail.trim();
    if (!email || !regPassword) {
      setError('請填 email 同密碼');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('請輸入正確的 email 格式');
      return;
    }
    if (regPassword.length < 6) {
      setError('密碼至少 6 位');
      return;
    }
    if (regPassword !== regConfirm) {
      setError('兩次輸入的密碼唔一致');
      return;
    }
    setBusy(true);
    try {
      const data = await apiClient<TokenPair>('/auth/register', {
        method: 'POST',
        auth: false,
        body: {
          email,
          password: regPassword,
          nickname: regNickname.trim() || null,
        },
      });
      saveAuth(data.access_token, data.refresh_token, data.user);
      router.push('/');
    } catch (err: unknown) {
      setError((err as { message?: string }).message ?? '註冊失敗');
    } finally {
      setBusy(false);
    }
  };

  // ---------- OTP 登入（備用） ----------
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
        <h1 className={styles.title}>{mode === 'login' ? '歡迎回來' : '建立帳號'}</h1>
        <p className={styles.subtitle}>
          {mode === 'login' ? '登入短劇平台' : '免費註冊，即刻睇劇'}
        </p>

        {error && <p className={styles.error}>{error}</p>}

        {mode === 'login' ? (
          <>
            {/* 帳號密碼登入（主要） */}
            <form onSubmit={handlePasswordLogin} className={styles.form}>
              <label className={styles.field}>
                <span>帳號（手機號碼或 email）</span>
                <input
                  type="text"
                  placeholder="85263106930 或 you@example.com"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className={styles.input}
                  autoComplete="username"
                />
              </label>
              <label className={styles.field}>
                <span>密碼</span>
                <input
                  type="password"
                  placeholder="請輸入密碼"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={styles.input}
                  autoComplete="current-password"
                />
              </label>
              <button type="submit" className={styles.primaryBtn} disabled={busy}>
                {busy ? '登入中…' : '登入'}
              </button>
            </form>

            {/* 切換去註冊 */}
            <div style={{ textAlign: 'center', marginTop: 14 }}>
              <button
                type="button"
                className={styles.toggleLink}
                onClick={() => {
                  setMode('register');
                  setError(null);
                }}
              >
                未註冊？立即註冊
              </button>
            </div>

            <div className={styles.divider}>
              <span className={styles.dividerLine} />
              <span className={styles.dividerText}>或</span>
              <span className={styles.dividerLine} />
            </div>

            <button
              type="button"
              className={styles.googleBtn}
              onClick={handleGoogleLogin}
              disabled={busy}
            >
              <GoogleIcon />
              使用 Google 帳號登入
            </button>

            {/* OTP 備用登入（可摺疊） */}
            <div className={styles.divider}>
              <span className={styles.dividerLine} />
              <button
                type="button"
                className={styles.toggleLink}
                onClick={() => setShowOtp((v) => !v)}
              >
                {showOtp ? '收起手機驗證碼登入' : '用手機驗證碼登入'}
              </button>
              <span className={styles.dividerLine} />
            </div>

            {showOtp && (
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
                    className={styles.ghostBtn}
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
                    <button type="submit" className={styles.ghostBtn} disabled={busy}>
                      {busy ? '驗證中…' : '驗證登入'}
                    </button>
                  </>
                )}
              </form>
            )}
          </>
        ) : (
          <>
            {/* 註冊表單 */}
            <form onSubmit={handleRegister} className={styles.form}>
              <label className={styles.field}>
                <span>Email *</span>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className={styles.input}
                  autoComplete="email"
                />
              </label>
              <label className={styles.field}>
                <span>密碼 *（至少 6 位）</span>
                <input
                  type="password"
                  placeholder="設定密碼"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className={styles.input}
                  autoComplete="new-password"
                />
              </label>
              <label className={styles.field}>
                <span>確認密碼 *</span>
                <input
                  type="password"
                  placeholder="再輸入一次密碼"
                  value={regConfirm}
                  onChange={(e) => setRegConfirm(e.target.value)}
                  className={styles.input}
                  autoComplete="new-password"
                />
              </label>
              <label className={styles.field}>
                <span>暱稱（選填）</span>
                <input
                  type="text"
                  placeholder="想點樣稱呼你"
                  value={regNickname}
                  onChange={(e) => setRegNickname(e.target.value)}
                  className={styles.input}
                  maxLength={64}
                />
              </label>
              <button type="submit" className={styles.primaryBtn} disabled={busy}>
                {busy ? '註冊中…' : '註冊並登入'}
              </button>
            </form>

            <div style={{ textAlign: 'center', marginTop: 14 }}>
              <button
                type="button"
                className={styles.toggleLink}
                onClick={() => {
                  setMode('login');
                  setError(null);
                }}
              >
                已有帳號？返回登入
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
