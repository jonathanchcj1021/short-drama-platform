'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/apiClient';
import type { Episode } from '@/types';
import styles from './page.module.css';

interface StreamResponse {
  video_url: string;
}

interface EpisodeDetail extends Episode {
  drama_title?: string;
  prev_episode_id?: number | null;
  next_episode_id?: number | null;
}

const REPORT_INTERVAL_MS = 10_000;

function PlayInner() {
  const router = useRouter();
  const [episodeId, setEpisodeId] = useState<string>('');

  // 靜態匯出下由查詢參數讀取集數 id（/play/?episode=1）
  useEffect(() => {
    setEpisodeId(new URLSearchParams(window.location.search).get('episode') ?? '');
  }, []);

  const videoRef = useRef<HTMLVideoElement>(null);
  const [episode, setEpisode] = useState<EpisodeDetail | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 拉集數資訊 + 串流位址
  const loadEpisode = () => {
    if (!episodeId) return;
    setLoading(true);
    setError(null);

    Promise.all([
      apiClient<EpisodeDetail>(`/episodes/${episodeId}`),
      apiClient<StreamResponse>(`/episodes/${episodeId}/stream`),
    ])
      .then(([ep, stream]) => {
        setEpisode(ep);
        setVideoUrl(stream.video_url);
      })
      .catch((e: { message?: string }) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEpisode();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [episodeId]);

  // 每 10 秒上報觀看進度
  useEffect(() => {
    if (!episodeId || !videoUrl) return;

    const report = async () => {
      const v = videoRef.current;
      if (!v) return;
      try {
        await apiClient(`/episodes/${episodeId}/progress`, {
          method: 'POST',
          body: {
            position_sec: Math.floor(v.currentTime),
            duration_sec: Math.floor(v.duration || 0),
          },
        });
      } catch {
        // 忽略單次上報失敗
      }
    };

    const timer = setInterval(report, REPORT_INTERVAL_MS);
    return () => {
      clearInterval(timer);
      // 離開時最後上報一次
      report();
    };
  }, [episodeId, videoUrl]);

  const goPrev = () => {
    if (episode?.prev_episode_id) router.push(`/play/?episode=${episode.prev_episode_id}`);
  };
  const goNext = () => {
    if (episode?.next_episode_id) router.push(`/play/?episode=${episode.next_episode_id}`);
  };

  if (loading) {
    return (
      <div className={styles.centerBox}>
        <div className={styles.spinner} />
      </div>
    );
  }
  if (error) {
    return (
      <div className={styles.centerBox}>
        <p className={styles.errorPill}>{error}</p>
        <button type="button" className={styles.retryBtn} onClick={loadEpisode}>
          重試
        </button>
      </div>
    );
  }

  return (
    <div className={styles.playerWrap}>
      <video
        ref={videoRef}
        src={videoUrl}
        controls
        autoPlay
        className={styles.video}
      />
      <div className={styles.info}>
        <h1 className={styles.title}>
          {episode?.drama_title ? `${episode.drama_title} · ` : ''}
          第 {episode?.episode_number} 集
        </h1>
        <p className={styles.epTitle}>{episode?.title}</p>
        <div className={styles.nav}>
          <button
            type="button"
            className={styles.navGhost}
            onClick={goPrev}
            disabled={!episode?.prev_episode_id}
          >
            上一集
          </button>
          <button
            type="button"
            className={styles.navPrimary}
            onClick={goNext}
            disabled={!episode?.next_episode_id}
          >
            下一集
          </button>
        </div>
      </div>
    </div>
  );
}

export default function PlayClient() {
  return (
    <ProtectedRoute>
      <PlayInner />
    </ProtectedRoute>
  );
}
