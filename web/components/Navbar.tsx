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

  return (
    <header className={styles.navbar}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>
          短劇平台
        </Link>
        <nav className={styles.right}>
          {loggedIn ? (
            <>
              <span className={styles.phone}>{user?.phone ?? '已登入'}</span>
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
