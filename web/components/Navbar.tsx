'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getUser, isLoggedIn, clearAuth } from '@/lib/auth';
import type { User } from '@/types';
import styles from './Navbar.module.css';

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    setUser(getUser());
    setLoggedIn(isLoggedIn());
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
