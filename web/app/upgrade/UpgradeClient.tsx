'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/apiClient';
import { formatVipExpiry, getUser, isVip, saveUser } from '@/lib/auth';
import type { BillingPlan, BillingStatus, User } from '@/types';
import styles from './page.module.css';

function UpgradeInner() {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [subscribing, setSubscribing] = useState<BillingPlan | null>(null);

  useEffect(() => {
    apiClient<BillingStatus>('/billing/me')
      .then((data) => setStatus(data))
      .catch((e: { message?: string }) => setError(e.message ?? '載入會員狀態失敗'))
      .finally(() => setLoading(false));
  }, []);

  const handleSubscribe = async (plan: BillingPlan) => {
    setError(null);
    setSubscribing(plan);
    try {
      const data = await apiClient<BillingStatus>('/billing/subscribe', {
        method: 'POST',
        query: { plan },
      });
      // 合併新會員欄位入本機 user（保留 phone / email / is_admin 等其他欄位）
      const me: User | null = getUser();
      if (me) {
        saveUser({
          ...me,
          membership_tier: data.membership_tier,
          vip_expires_at: data.vip_expires_at,
          is_vip: data.is_vip,
        });
      }
      setStatus(data);
      window.dispatchEvent(new Event('auth-changed'));
    } catch (e: unknown) {
      setError((e as { message?: string }).message ?? '升級失敗，請重試');
    } finally {
      setSubscribing(null);
    }
  };

  if (loading) {
    return (
      <div className={styles.wrap}>
        <div className={styles.centerBox}>
          <div className={styles.spinner} />
        </div>
      </div>
    );
  }

  const me = getUser();
  const vipNow = isVip(me) || (status?.is_vip ?? false);
  const monthlyPrice = status?.monthly_price_hkd ?? 28;
  const yearlyPrice = status?.yearly_price_hkd ?? 288;

  return (
    <div className={styles.wrap}>
      <div className={styles.container}>
        <Link href="/" className={styles.backLink}>
          ‹ 返回首頁
        </Link>

        <h1 className={styles.title}>升級 VIP</h1>
        <p className={styles.subtitle}>
          VIP 會員全部劇集任睇，免睇廣告，即開即睇。
        </p>

        {error && <p className={styles.error}>{error}</p>}

        {vipNow && (
          <div className={styles.vipBanner}>
            <span className={styles.vipBadge}>VIP</span>
            <span>
              你係 VIP
              {me?.vip_expires_at ? ` · 到期日 ${formatVipExpiry(me)}` : ''}
            </span>
          </div>
        )}

        <div className={styles.plans}>
          <div className={styles.planCard}>
            <h2 className={styles.planName}>月費</h2>
            <p className={styles.planPrice}>
              HK${monthlyPrice}
              <span className={styles.planPeriod}>/ 月</span>
            </p>
            <ul className={styles.planFeatures}>
              <li>全部劇集任睇</li>
              <li>免睇廣告</li>
              <li>隨時取消</li>
            </ul>
            <button
              type="button"
              className={styles.planBtn}
              disabled={vipNow || subscribing !== null}
              onClick={() => handleSubscribe('monthly')}
            >
              {subscribing === 'monthly'
                ? '處理中…'
                : vipNow
                  ? '你已是 VIP'
                  : '升級月費 VIP'}
            </button>
          </div>

          <div className={`${styles.planCard} ${styles.planCardFeatured}`}>
            <span className={styles.featuredTag}>最抵</span>
            <h2 className={styles.planName}>年費</h2>
            <p className={styles.planPrice}>
              HK${yearlyPrice}
              <span className={styles.planPeriod}>/ 年</span>
            </p>
            <p className={styles.saveNote}>
              慳 HK${monthlyPrice * 12 - yearlyPrice}（相當於 2 個月免費）
            </p>
            <ul className={styles.planFeatures}>
              <li>全部劇集任睇</li>
              <li>免睇廣告</li>
              <li>最長保證觀看</li>
            </ul>
            <button
              type="button"
              className={styles.planBtn}
              disabled={vipNow || subscribing !== null}
              onClick={() => handleSubscribe('yearly')}
            >
              {subscribing === 'yearly'
                ? '處理中…'
                : vipNow
                  ? '你已是 VIP'
                  : '升級年費 VIP'}
            </button>
          </div>
        </div>

        <p className={styles.footnote}>
          * 呢個示範環境用模擬付款，唔會真係收費；升級後即時生效。
        </p>
      </div>
    </div>
  );
}

export default function UpgradePage() {
  return (
    <ProtectedRoute>
      <UpgradeInner />
    </ProtectedRoute>
  );
}
