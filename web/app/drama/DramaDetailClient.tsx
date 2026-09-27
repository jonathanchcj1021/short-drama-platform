'use client';

import { useEffect, useMemo, useState } from 'react';
import EpisodeList from '@/components/EpisodeList';
import { apiClient } from '@/lib/apiClient';
import { isLoggedIn } from '@/lib/auth';
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

  useEffect(() => {
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
  }, [id]);

  // 已觀看集數對照表
  const progressMap = useMemo(() => {
    const map: Record<number, number> = {};
    if (progress) map[progress.episodeId] = progress.positionSec;
    return map;
  }, [progress]);

  if (loading) return <main className="container"><p className={styles.hint}>載入中…</p></main>;
  if (error) return <main className="container"><p className={styles.error}>{error}</p></main>;
  if (!drama) return <main className="container"><p className={styles.hint}>找不到劇集</p></main>;

  return (
    <main className="container">
      <div className={styles.header}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={drama.coverUrl || '/favicon.ico'} alt={drama.title} className={styles.cover} />
        <div className={styles.info}>
          <h1 className={styles.title}>{drama.title}</h1>
          <p className={styles.meta}>
            <span className={styles.tag}>{drama.category?.name ?? drama.categoryName ?? '未分類'}</span>
            <span>{drama.episodeCount} 集</span>
          </p>
          <p className={styles.desc}>{drama.description}</p>
          {progress && (
            <p className={styles.progress}>
              上次看到：第 {drama.episodes.find((e) => e.id === progress.episodeId)?.episodeNumber ?? '?'} 集
              （{Math.floor(progress.positionSec)}s）
            </p>
          )}
        </div>
      </div>

      <h2 className={styles.sectionTitle}>集數列表</h2>
      <EpisodeList
        episodes={drama.episodes ?? []}
        currentEpisodeId={progress?.episodeId}
        progressMap={progressMap}
      />
    </main>
  );
}
