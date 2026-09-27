'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState, type ReactNode } from 'react';
import { isLoggedIn } from '@/lib/auth';
import styles from './ProtectedRoute.module.css';

interface Props {
  children: ReactNode;
}

/** 需登入頁面的包裝元件：未登入則跳轉 /login */
export default function ProtectedRoute({ children }: Props) {
  const router = useRouter();
  const [checked, setChecked] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    const ok = isLoggedIn();
    setAuthed(ok);
    setChecked(true);
    if (!ok) {
      router.replace('/login');
    }
  }, [router]);

  if (!checked) {
    return (
      <div className={styles.wrap}>
        <div className={styles.spinner} />
        <p className={styles.text}>載入中…</p>
      </div>
    );
  }
  if (!authed) {
    return (
      <div className={styles.wrap}>
        <div className={styles.spinner} />
        <p className={styles.text}>即將跳轉登入頁…</p>
      </div>
    );
  }
  return <>{children}</>;
}
