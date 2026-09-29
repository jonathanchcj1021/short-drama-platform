'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getUser, isLoggedIn, clearAuth, isVip, formatVipExpiry } from '@/lib/auth';
import type { User } from '@/types';
import styles from './Navbar.module.css';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [loggedIn, setLoggedIn] = useState(false);

  // Navbar 喺 root layout，client-side 轉頁時唔會 remount。
  // 所以每當 route（pathname）改變，都重新讀一次 localStorage，
  // 避免登入 / 登出之後 UI 仲停留在舊狀態。
  useEffect(() => {
    setUser(getUser());
    setLoggedIn(isLoggedIn());
  }, [pathname]);

  // App 啟動 bootstrapSession 完成後會 broadcast auth-changed（例如 refresh token 續返成功），
  // 此時都要重新讀 localStorage，令 Navbar 由「未登入」更新做「已登入」。
  useEffect(() => {
    const sync = () => {
      setUser(getUser());
      setLoggedIn(isLoggedIn());
    };
    window.addEventListener('auth-changed', sync);
    return () => window.removeEventListener('auth-changed', sync);
  }, []);

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    setLoggedIn(false);
    router.push('/');
  };

  const displayPhone = user?.phone ?? user?.phone_number ?? '';

  return (
    <header className={styles.navbar}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>
          <span className={styles.logoMark} aria-hidden />
          <span className={styles.brandText}>短劇平台</span>
        </Link>
        <nav className={styles.right}>
          {loggedIn ? (
            <>
              {user?.is_admin && (
                <Link href="/admin" className={styles.adminLink}>
                  管理
                </Link>
              )}
              {isVip(user) ? (
                <span className={styles.vipBadge} title="VIP 會員">
                  VIP · 到期 {formatVipExpiry(user)}
                </span>
              ) : (
                <>
                  <span className={styles.freeBadge}>免費會員</span>
                  <Link href="/upgrade" className={styles.upgradeLink}>
                    升級 VIP
                  </Link>
                </>
              )}
              {displayPhone && <span className={styles.phone}>{displayPhone}</span>}
              <button type="button" className={styles.logoutBtn} onClick={handleLogout}>
                登出
              </button>
            </>
          ) : (
            <Link href="/login" className={styles.loginBtn}>
              登入
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
