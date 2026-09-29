'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import DramaCard from '@/components/DramaCard';
import PosterPlaceholder from '@/components/PosterPlaceholder';
import { apiClient } from '@/lib/apiClient';
import type { Category, DramaListItem, DramaListPage } from '@/types';
import styles from './page.module.css';

const PAGE_SIZE = 24;
const MAX_PAGE_BUTTONS = 7;

/** 來源 filter 選項（映射 web/lib/sources.ts） */
const SOURCE_TABS: { label: string; value: string | undefined }[] = [
  { label: '全部來源', value: undefined },
  { label: '紅果短劇', value: 'hongguo' },
  { label: '優酷短劇', value: 'youku' },
  { label: 'YouTube', value: 'youtube' },
];

/** 頁碼 window：最多 MAX_PAGE_BUTTONS 個，頭尾保留＋省略號 */
function buildPageItems(current: number, total: number): (number | 'ellipsis')[] {
  if (total <= MAX_PAGE_BUTTONS) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const pages = new Set<number>([1, total, current, current - 1, current + 1]);
  const sorted = [...pages].filter((p) => p >= 1 && p <= total).sort((a, b) => a - b);
  const out: (number | 'ellipsis')[] = [];
  let prev = 0;
  for (const p of sorted) {
    if (p - prev > 1) out.push('ellipsis');
    out.push(p);
    prev = p;
  }
  return out;
}

export default function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [page, setPage] = useState(1);
  const [activeCategory, setActiveCategory] = useState<number | undefined>(undefined);
  const [activeSource, setActiveSource] = useState<string | undefined>(undefined);
  const [data, setData] = useState<DramaListPage | null>(null);
  const [featured, setFeatured] = useState<DramaListItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const noFilter = activeCategory === undefined && activeSource === undefined;

  // 拉分類列表
  useEffect(() => {
    apiClient<Category[]>('/categories', { auth: false })
      .then((d) => setCategories(d ?? []))
      .catch(() => setCategories([]));
  }, []);

  // 拉劇集列表（分頁＋分類＋來源）
  const fetchDramas = useCallback(() => {
    setLoading(true);
    setError(null);
    apiClient<DramaListPage>('/dramas', {
      auth: false,
      query: {
        page,
        page_size: PAGE_SIZE,
        category_id: activeCategory,
        source: activeSource,
      },
    })
      .then((d) => setData(d ?? { items: [], total: 0, page: 1, page_size: PAGE_SIZE, total_pages: 1 }))
      .catch((e: { message?: string }) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false));
  }, [page, activeCategory, activeSource]);

  useEffect(() => {
    fetchDramas();
  }, [fetchDramas]);

  // Hero 精選：獨立攞最新一部（page=1&page_size=1），只喺無 filter 時先拉
  useEffect(() => {
    if (!noFilter) {
      setFeatured(null);
      return;
    }
    apiClient<DramaListPage>('/dramas', {
      auth: false,
      query: { page: 1, page_size: 1 },
    })
      .then((d) => setFeatured(d?.items?.[0] ?? null))
      .catch(() => setFeatured(null));
  }, [noFilter]);

  // 分類／來源變更 → reset 返第 1 頁
  const selectCategory = (id: number | undefined) => {
    setActiveCategory(id);
    setPage(1);
  };
  const selectSource = (src: string | undefined) => {
    setActiveSource(src);
    setPage(1);
  };
  const gotoPage = (n: number) => {
    if (n === page) return;
    setPage(n);
    window.scrollTo({ top: 0 });
  };

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = data?.total_pages ?? 1;
  const showHero = noFilter && !loading && !error && featured != null;
  const pageItems = buildPageItems(page, totalPages);

  return (
    <main className="container">
      <div className={styles.pageHead}>
        <h1 className={styles.pageTitle}>短劇精選</h1>
        <p className={styles.pageSub}>熱門好劇，一集接一集</p>
      </div>

      {/* ===== Hero 區（精選劇集，無分類／來源 filter 先顯示） ===== */}
      {showHero && featured && (
        <section className={styles.hero}>
          {featured.cover_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={featured.cover_url} alt={featured.title} className={styles.heroBg} />
          ) : (
            <PosterPlaceholder title={featured.title} className={styles.heroBg} />
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

      {/* ===== 來源篩選 tab ===== */}
      <div className={styles.sourceTabs}>
        {SOURCE_TABS.map((t) => (
          <button
            key={t.label}
            type="button"
            className={`${styles.sourceTab} ${activeSource === t.value ? styles.sourceTabActive : ''}`}
            onClick={() => selectSource(t.value)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ===== 分類篩選 tab ===== */}
      <div className={styles.tabs}>
        <button
          type="button"
          className={`${styles.tab} ${activeCategory === undefined ? styles.tabActive : ''}`}
          onClick={() => selectCategory(undefined)}
        >
          全部
        </button>
        {categories.map((c) => (
          <button
            key={c.id}
            type="button"
            className={`${styles.tab} ${activeCategory === c.id ? styles.tabActive : ''}`}
            onClick={() => selectCategory(c.id)}
          >
            {c.name}
          </button>
        ))}
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className={styles.grid}>
          {Array.from({ length: 12 }).map((_, i) => (
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
      {!loading && !error && items.length === 0 && (
        <div className={styles.stateBox}>
          <div className={styles.emptyIcon} aria-hidden />
          <p className={styles.emptyTitle}>目前沒有劇集</p>
          <p className={styles.emptySub}>稍後再回來看看</p>
        </div>
      )}

      {/* Grid */}
      {!loading && !error && items.length > 0 && (
        <>
          <div className={styles.grid}>
            {items.map((d) => (
              <DramaCard key={d.id} drama={d} />
            ))}
          </div>

          {/* ===== 分頁控制 ===== */}
          {totalPages > 1 && (
            <div className={styles.pager}>
              <p className={styles.pagerCount}>
                共 {total} 部 · 第 {page} / {totalPages} 頁
              </p>
              <div className={styles.pagerRow}>
                <button
                  type="button"
                  className={styles.pagerBtn}
                  disabled={page <= 1}
                  onClick={() => gotoPage(page - 1)}
                >
                  ‹ 上一頁
                </button>
                <div className={styles.pagerPages}>
                  {pageItems.map((p, i) =>
                    p === 'ellipsis' ? (
                      <span key={`e${i}`} className={styles.pagerEllipsis}>
                        …
                      </span>
                    ) : (
                      <button
                        key={p}
                        type="button"
                        className={`${styles.pagerPage} ${p === page ? styles.pagerPageActive : ''}`}
                        onClick={() => gotoPage(p)}
                      >
                        {p}
                      </button>
                    ),
                  )}
                </div>
                <button
                  type="button"
                  className={styles.pagerBtn}
                  disabled={page >= totalPages}
                  onClick={() => gotoPage(page + 1)}
                >
                  下一頁 ›
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </main>
  );
}
