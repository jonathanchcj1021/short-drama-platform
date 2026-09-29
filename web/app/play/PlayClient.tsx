'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import { apiClient } from '@/lib/apiClient';
import type { DramaDetail, Episode } from '@/types';
import styles from './page.module.css';

interface StreamResponse {
  video_url: string;
  /** false = 呢集冇真片，要顯示「敬請期待」占位（唔好黑畫面） */
  available?: boolean;
  message?: string | null;
  /** true = 免費用戶要睇 20 秒廣告先解鎖；此時 available=true 但 video_url 為空 */
  requires_ad?: boolean;
}

interface EpisodeDetail extends Episode {
  drama_title?: string;
  prev_episode_id?: number | null;
  next_episode_id?: number | null;
}

const REPORT_INTERVAL_MS = 10_000;
const AD_SECONDS = 20;

/** 模擬廣告 creative（純視覺輪播，唔接真廣告聯盟） */
const AD_CREATIVES = [
  { emoji: '🍜', title: '阿華車仔麵', sub: '深夜食堂，街坊至愛' },
  { emoji: '📱', title: '全城最平數據卡', sub: '月費 HK$38 起，無限速' },
  { emoji: '🏠', title: '搵樓平台', sub: '免佣放盤，一分鐘上架' },
];

function PlayInner() {
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

  // ===== 廣告閘狀態 =====
  // adMode=true 時：顯示全畫面廣告 overlay，唔好 autoplay 真片。
  const [adMode, setAdMode] = useState(false);
  const [adCountdown, setAdCountdown] = useState(AD_SECONDS);
  const [adUnlocking, setAdUnlocking] = useState(false);
  const [adError, setAdError] = useState<string | null>(null);

  // 拉集數資訊 + 串流位址
  const loadEpisode = useCallback(() => {
    if (!episodeId) return;
    setLoading(true);
    setError(null);
    setComingSoon(false);
    setVideoError(false);
    setAdError(null);

    Promise.all([
      apiClient<EpisodeDetail>(`/episodes/${episodeId}`),
      apiClient<StreamResponse>(`/episodes/${episodeId}/stream`),
    ])
      .then(async ([ep, stream]) => {
        // 後端 /episodes/{id} 冇直接回傳 prev/next/drama_title，
        // 用 drama_id 拉劇集詳情，自己喺 episodes list 度計上下集 id。
        try {
          const drama = await apiClient<DramaDetail>(`/dramas/${ep.drama_id}`);
          const list = drama.episodes ?? [];
          const idx = list.findIndex((e) => e.id === ep.id);
          const prev = idx > 0 ? list[idx - 1].id : null;
          const next = idx >= 0 && idx < list.length - 1 ? list[idx + 1].id : null;
          setEpisode({
            ...ep,
            drama_title: drama.title,
            prev_episode_id: prev,
            next_episode_id: next,
          });
        } catch {
          // drama 拉唔到都照播，只係冇上下集掣（等同舊行為）
          setEpisode(ep);
        }
        // 後端話呢集冇片：唔好 setVideoUrl（避免黑畫面），改顯示占位。
        if (stream.available === false) {
          setComingSoon(true);
          setVideoUrl('');
          setAdMode(false);
          return;
        }
        // 後端要求睇廣告：進入廣告模式，唔 setVideoUrl
        if (stream.requires_ad === true) {
          setVideoUrl('');
          setAdCountdown(AD_SECONDS);
          setAdMode(true);
          return;
        }
        // 正常：直接播
        setAdMode(false);
        setVideoUrl(stream.video_url);
      })
      .catch((e: { message?: string }) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false));
  }, [episodeId]);

  useEffect(() => {
    loadEpisode();
  }, [loadEpisode]);

  // ===== 廣告倒數 =====
  // adMode=true 時每秒減一；到 0 自動 POST unlock，再 reload stream 攞真片。
  useEffect(() => {
    if (!adMode) return;
    setAdCountdown(AD_SECONDS);
    setAdUnlocking(false);

    const timer = window.setInterval(() => {
      setAdCountdown((prev) => {
        if (prev <= 1) {
          window.clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [adMode, episodeId]);

  // 倒數到 0 → 解鎖呢集
  useEffect(() => {
    if (!adMode || adCountdown !== 0 || adUnlocking) return;
    let cancelled = false;
    setAdUnlocking(true);
    (async () => {
      try {
        await apiClient(`/episodes/${episodeId}/unlock`, { method: 'POST' });
        if (cancelled) return;
        // 解鎖成功：離開廣告模式，重新 load（呢次 stream 會有 video_url）
        setAdMode(false);
        loadEpisode();
      } catch (e: unknown) {
        if (cancelled) return;
        setAdError((e as { message?: string }).message ?? '解鎖失敗，請重試');
        setAdUnlocking(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [adMode, adCountdown, adUnlocking, episodeId, loadEpisode]);

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

  // 切集：直接 setEpisodeId，等依賴 [episodeId] 嘅 loadEpisode() 重新切片；
  // 唔好用 router.push('/play/?episode=X')，因為 Next.js App Router 唔會重新 mount
  // 同一個 page component，useEffect([]) 唔會再跑，URL 變咗但片仲係舊集。
  const goPrev = () => {
    const target = episode?.prev_episode_id;
    if (!target) return;
    setEpisodeId(String(target));
    window.history.replaceState(null, '', `${window.location.pathname}?episode=${target}`);
  };
  const goNext = () => {
    const target = episode?.next_episode_id;
    if (!target) return;
    setEpisodeId(String(target));
    window.history.replaceState(null, '', `${window.location.pathname}?episode=${target}`);
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

  // ===== 廣告模式：全畫面 overlay，唔播真片 =====
  if (adMode) {
    const creative = AD_CREATIVES[Math.floor((AD_SECONDS - adCountdown) / 7) % AD_CREATIVES.length];
    return (
      <div className={styles.stage}>
        <div className={styles.phone}>
          <div className={styles.adOverlay}>
            <div className={styles.adTag}>廣告</div>
            <div className={styles.adCreative} aria-hidden>
              <div className={styles.adCreativeEmoji}>{creative.emoji}</div>
              <div className={styles.adCreativeTitle}>{creative.title}</div>
              <div className={styles.adCreativeSub}>{creative.sub}</div>
            </div>
            <div className={styles.adCountdown}>{adCountdown}</div>
            <p className={styles.adHint}>
              {adUnlocking
                ? '解鎖中…'
                : `觀看 ${AD_SECONDS} 秒廣告，免費解鎖第 ${episode?.episode_number ?? ''} 集`}
            </p>
            {adError && (
              <>
                <p className={styles.adError}>{adError}</p>
                <button
                  type="button"
                  className={styles.retryBtn}
                  onClick={() => {
                    setAdError(null);
                    setAdUnlocking(false);
                    setAdCountdown(AD_SECONDS);
                  }}
                >
                  重試
                </button>
              </>
            )}
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
