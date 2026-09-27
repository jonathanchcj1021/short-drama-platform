'use client';

import { useEffect, useState } from 'react';
import DramaCard from '@/components/DramaCard';
import { apiClient } from '@/lib/apiClient';
import type { Category, Drama } from '@/types';
import styles from './page.module.css';

export default function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [dramas, setDramas] = useState<Drama[]>([]);
  const [activeCategory, setActiveCategory] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 拉分類列表
  useEffect(() => {
    apiClient<Category[]>('/categories', { auth: false })
      .then((data) => setCategories(data ?? []))
      .catch(() => setCategories([]));
  }, []);

  // 拉劇集列表（依分類篩選）
  useEffect(() => {
    setLoading(true);
    setError(null);
    apiClient<Drama[]>('/dramas', {
      auth: false,
      query: activeCategory !== undefined ? { category: activeCategory } : undefined,
    })
      .then((data) => setDramas(data ?? []))
      .catch((e: { message?: string }) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false));
  }, [activeCategory]);

  return (
    <main className="container">
      {/* 分類篩選 tab */}
      <div className={styles.tabs}>
        <button
          type="button"
          className={`${styles.tab} ${activeCategory === undefined ? styles.tabActive : ''}`}
          onClick={() => setActiveCategory(undefined)}
        >
          全部
        </button>
        {categories.map((c) => (
          <button
            key={c.id}
            type="button"
            className={`${styles.tab} ${activeCategory === c.id ? styles.tabActive : ''}`}
            onClick={() => setActiveCategory(c.id)}
          >
            {c.name}
          </button>
        ))}
      </div>

      {loading && <p className={styles.hint}>載入中…</p>}
      {error && <p className={styles.error}>{error}</p>}
      {!loading && !error && dramas.length === 0 && (
        <p className={styles.hint}>目前沒有劇集</p>
      )}

      <div className={styles.grid}>
        {dramas.map((d) => (
          <DramaCard key={d.id} drama={d} />
        ))}
      </div>
    </main>
  );
}
