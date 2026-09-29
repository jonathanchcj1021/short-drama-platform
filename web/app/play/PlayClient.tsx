'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/apiClient';
import type { Episode } from '@/types';
import styles from './page.module.css';

interface StreamResponse {
  video_url: string;
  /** false = 呢集冇真片，要顯示「敬請期待」占位（唔好黑畫面） */
  available?: boolean;
  message?: string | null;
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
  // 呢集冇真片（後端 available=false）→ 顯示「敬請期待」海報
  const [comingSoon, setComingSoon] = useState(false);
  // <video> 自己播唔到（例如 CDN 唔穩定）→ 顯示重試，唔好黑畫面
  const [videoError, setVideoError] = useState(false);

  // 拉集數資訊 + 串流位址
  const loadEpisode = () => {
    if (!episodeId) return;
    setLoading(true);
    setError(null);
    setComingSoon(false);
    setVideoError(false);

    Promise.all([
      apiClient<EpisodeDetail>(`/episodes/${episodeId}`),
      apiClient<StreamResponse>(`/episodes/${episodeId}/stream`),
    ])
      .then(([ep, stream]) => {
        setEpisode(ep);
        // 後端話呢集冇片：唔好 setVideoUrl（避免黑畫面），改顯示占位。
        if (stream.available === false) {
          setComingSoon(true);
          setVideoUrl('');
          return;
        }
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

  // 呢集仲未有片：優雅「敬請期待」海報，唔好黑畫面。
  if (comingSoon) {
    return (
      <div className={styles.stage}>
        <div className={styles.phone}>
          <div className={styles.topBar}>
            <Link href={episode?.drama_id ? `/drama/?id=${episode.drama_id}` : '/'} className={styles.backBtn}>
              ‹ 返回
            </Link>
            <span className={styles.topTitle}>
              {episode?.drama_title ? episode.drama_title : '播放'}
            </span>
          </div>
          <div className={styles.centerBox}>
            <p className={styles.comingSoonEmoji} aria-hidden>🎬</p>
            <p className={styles.comingSoonTitle}>敬請期待</p>
            <p className={styles.comingSoonSub}>此集暫時未能播放，將於稍後上線</p>
            <button type="button" className={styles.retryBtn} onClick={loadEpisode}>
              重新整理
            </button>
          </div>
          <div className={styles.bottomBar}>
            <h1 className={styles.title}>第 {episode?.episode_number} 集</h1>
            <p className={styles.epTitle}>{episode?.title}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.stage}>
      <div className={styles.phone}>
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          autoPlay
          playsInline
          className={styles.video}
          onError={() => setVideoError(true)}
        />

        {/* 影片出錯（CDN 唔穩定等）：遮蓋住黑畫面，俾人重試 */}
        {videoError && (
          <div className={styles.centerBox}>
            <p className={styles.errorPill}>此集暫時無法播放，敬請期待</p>
            <button
              type="button"
              className={styles.retryBtn}
              onClick={() => {
                setVideoError(false);
                loadEpisode();
              }}
            >
              重試
            </button>
          </div>
        )}

        {/* 頂部 overlay：返回 + 標題 */}
        <div className={styles.topBar}>
          <Link href={episode?.drama_id ? `/drama/?id=${episode.drama_id}` : '/'} className={styles.backBtn}>
            ‹ 返回
          </Link>
          <span className={styles.topTitle}>
            {episode?.drama_title ? episode.drama_title : '播放中'}
          </span>
        </div>

        {/* 左右浮動切集（桌面） */}
        <button
          type="button"
          className={`${styles.sideBtn} ${styles.sidePrev}`}
          onClick={goPrev}
          disabled={!episode?.prev_episode_id}
          aria-label="上一集"
        >
          ‹
        </button>
        <button
          type="button"
          className={`${styles.sideBtn} ${styles.sideNext}`}
          onClick={goNext}
          disabled={!episode?.next_episode_id}
          aria-label="下一集"
        >
          ›
        </button>

        {/* 底部 overlay：集名 + 上下集 */}
        <div className={styles.bottomBar}>
          <h1 className={styles.title}>第 {episode?.episode_number} 集</h1>
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
