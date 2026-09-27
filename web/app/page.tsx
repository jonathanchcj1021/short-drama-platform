'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
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
  const fetchDramas = useCallback(() => {
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

  useEffect(() => {
    fetchDramas();
  }, [fetchDramas]);

  const featured = !loading && !error && dramas.length > 0 ? dramas[0] : null;
  const showHero = featured && activeCategory === undefined;

  return (
    <main className="container">
      {/* ===== Hero 區（精選劇集，取 dramas[0]） ===== */}
      {showHero && (
        <section className={styles.hero}>
          {featured.cover_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={featured.cover_url} alt={featured.title} className={styles.heroBg} />
          )}
          <div className={styles.heroScrimX} />
          <div className={styles.heroScrimBottom} />
          <div className={styles.heroContent}>
            <span className={styles.heroChip}>
              {featured.category?.name ?? featured.category_name ?? '未分類'}
            </span>
            <h1 className={styles.heroTitle}>{featured.title}</h1>
            <p className={styles.heroDesc}>{featured.description}</p>
            <div className={styles.heroCtas}>
              <Link href={`/drama/?id=${featured.id}`} className={styles.heroPrimary}>
                ▶ 立即觀看
              </Link>
              <Link href={`/drama/?id=${featured.id}`} className={styles.heroGhost}>
                查看詳情
              </Link>
            </div>
          </div>
        </section>
      )}

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

      {/* Loading skeleton */}
      {loading && (
        <div className={styles.grid}>
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className={styles.skeletonCard}>
              <div className={`skeleton ${styles.skeletonCover}`} />
              <div className={`skeleton ${styles.skeletonLine}`} />
              <div className={`skeleton ${styles.skeletonLineSm}`} />
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className={styles.stateBox}>
          <p className={styles.errorPill}>{error}</p>
          <button type="button" className={styles.retryBtn} onClick={fetchDramas}>
            重試
          </button>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && dramas.length === 0 && (
        <div className={styles.stateBox}>
          <div className={styles.emptyIcon} aria-hidden />
          <p className={styles.emptyTitle}>目前沒有劇集</p>
          <p className={styles.emptySub}>稍後再回來看看</p>
        </div>
      )}

      {/* Grid */}
      {!loading && !error && dramas.length > 0 && (
        <div className={styles.grid}>
          {dramas.map((d) => (
            <DramaCard key={d.id} drama={d} />
          ))}
        </div>
      )}
    </main>
  );
}
