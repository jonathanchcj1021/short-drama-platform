'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import EpisodeList from '@/components/EpisodeList';
import PosterPlaceholder from '@/components/PosterPlaceholder';
import { apiClient } from '@/lib/apiClient';
import { isLoggedIn } from '@/lib/auth';
import { sourceLabel } from '@/lib/sources';
import type { DramaDetail, Progress } from '@/types';
import styles from './page.module.css';

export default function DramaDetailClient() {
  const [id, setId] = useState<string>('');

  // 靜態匯出下由查詢參數讀取劇集 id（/drama/?id=1），新劇無需重新 build
  useEffect(() => {
    setId(new URLSearchParams(window.location.search).get('id') ?? '');
  }, []);

  const [drama, setDrama] = useState<DramaDetail | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDrama = () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    apiClient<DramaDetail>(`/dramas/${id}`, { auth: false })
      .then((data) => {
        setDrama(data);
        // 已登入才拉觀看進度
        if (isLoggedIn()) {
          apiClient<Progress>(`/dramas/${id}/progress`)
            .then((p) => setProgress(p))
            .catch(() => setProgress(null));
        }
      })
      .catch((e: { message?: string }) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDrama();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // 已觀看集數對照表
  const progressMap = useMemo(() => {
    const map: Record<number, number> = {};
    if (progress) map[progress.episode_id] = progress.position_sec;
    return map;
  }, [progress]);

  // 開始觀看：有進度跳上次集數，否則跳第一集
  const firstEpisodeId = drama?.episodes?.[0]?.id;
  const resumeEpisodeId = progress?.episode_id ?? firstEpisodeId;

  if (loading) {
    return (
      <main className="container">
        <div className={styles.centerBox}>
          <div className={styles.spinner} />
        </div>
      </main>
    );
  }
  if (error) {
    return (
      <main className="container">
        <div className={styles.centerBox}>
          <p className={styles.errorPill}>{error}</p>
          <button type="button" className={styles.retryBtn} onClick={loadDrama}>
            重試
          </button>
        </div>
      </main>
    );
  }
  if (!drama) {
    return (
      <main className="container">
        <div className={styles.centerBox}>
          <p className={styles.emptyTitle}>找不到劇集</p>
        </div>
      </main>
    );
  }

  const categoryLabel = drama.category?.name ?? drama.category_name ?? '未分類';
  const from = sourceLabel(drama.source);
  const lastEpisodeNum = progress
    ? drama.episodes.find((e) => e.id === progress.episode_id)?.episode_number
    : null;

  return (
    <main className="container">
      {/* 朦朧封面背景 */}
      {drama.cover_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={drama.cover_url} alt="" className={styles.backdrop} aria-hidden />
      )}
      <div className={styles.backdropScrim} />

      <div className={styles.header}>
        {drama.cover_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={drama.cover_url} alt={drama.title} className={styles.cover} />
        ) : (
          <PosterPlaceholder title={drama.title} className={styles.cover} />
        )}
        <div className={styles.info}>
          <Link href="/" className={styles.backLink}>
            ← 返回
          </Link>
          <h1 className={styles.title}>{drama.title}</h1>
          <div className={styles.tags}>
            <span className={styles.tag}>{categoryLabel}</span>
            {drama.episode_count != null && <span className={styles.tag}>{drama.episode_count} 集</span>}
            {drama.release_year != null && <span className={styles.tag}>{drama.release_year}</span>}
            {drama.is_completed && <span className={styles.tagGold}>已完結</span>}
            {from && <span className={styles.tagGold}>來自：{from}</span>}
          </div>
          <p className={styles.desc}>{drama.description}</p>
          {progress && lastEpisodeNum != null && (
            <p className={styles.progressPill}>上次看到：第 {lastEpisodeNum} 集</p>
          )}
          {resumeEpisodeId != null && (
            <Link href={`/play/?episode=${resumeEpisodeId}`} className={styles.cta}>
              ▶ {progress ? '繼續觀看' : '開始觀看'}
            </Link>
          )}
        </div>
      </div>

      <h2 className={styles.sectionTitle}>劇集</h2>
      <EpisodeList
        episodes={drama.episodes ?? []}
        currentEpisodeId={progress?.episode_id}
        progressMap={progressMap}
      />
    </main>
  );
}
