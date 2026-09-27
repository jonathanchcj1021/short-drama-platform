'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/apiClient';
import { saveAuth } from '@/lib/auth';
import type { OtpRequestResponse, OtpVerifyResponse } from '@/types';
import styles from './page.module.css';

const COOLDOWN_SEC = 60;

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 倒數計時
  useEffect(() => {
    if (countdown <= 0) return;
    const t = setTimeout(() => setCountdown((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const handleSendOtp = async () => {
    setError(null);
    if (!/^1\d{10}$/.test(phone.trim())) {
      setError('請輸入正確的 11 位手機號碼');
      return;
    }
    setBusy(true);
    try {
      await apiClient<OtpRequestResponse>('/auth/otp/request', {
        method: 'POST',
        auth: false,
        body: { phone: phone.trim() },
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
        body: { phone: phone.trim(), code: otp.trim() },
      });
      saveAuth(data.accessToken, data.refreshToken, data.user);
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
        <h1 className={styles.title}>登入</h1>
        <p className={styles.subtitle}>手機號碼驗證碼登入</p>

        {error && <p className={styles.error}>{error}</p>}

        <form onSubmit={handleVerify} className={styles.form}>
          <label className={styles.field}>
            <span>手機號碼</span>
            <input
              type="tel"
              inputMode="numeric"
              placeholder="請輸入手機號碼"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
              maxLength={11}
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
