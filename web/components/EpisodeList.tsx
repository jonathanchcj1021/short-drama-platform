'use client';

import Link from 'next/link';
import type { Episode } from '@/types';
import styles from './EpisodeList.module.css';

interface Props {
  episodes: Episode[];
  /** 目前觀看到的 episodeId（用於標記已觀看／正在播放） */
  currentEpisodeId?: number;
  /** 觀看進度對照表：episodeId -> positionSec */
  progressMap?: Record<number, number>;
  /** 目前用家是否有效 VIP（VIP 唔使睇廣告，全部解鎖） */
  isVip?: boolean;
  /** 呢套劇係咪收費劇（false = 免費劇，全部集數任睇） */
  isPaidDrama?: boolean;
  /** 空集數時嘅標題（例如「暫時未有片源」）；唔傳就用預設「尚無集數」 */
  emptyTitle?: string;
  /** 空集數時嘅副提示（caller 自訂靚版 empty state） */
  emptyHint?: string;
}

const FREE_EPISODE_LIMIT = 10;

export default function EpisodeList({
  episodes,
  currentEpisodeId,
  progressMap = {},
  isVip = false,
  isPaidDrama = true,
  emptyTitle,
  emptyHint,
}: Props) {
  if (!episodes || episodes.length === 0) {
    if (emptyTitle) {
      return (
        <div className={styles.emptyBox}>
          <div className={styles.emptyIcon} aria-hidden />
          <p className={styles.emptyTitle}>{emptyTitle}</p>
          {emptyHint && <p className={styles.emptyHint}>{emptyHint}</p>}
        </div>
      );
    }
    return <p className={styles.empty}>尚無集數</p>;
  }

  return (
    <ul className={styles.list}>
      {episodes.map((ep) => {
        const watched = progressMap[ep.id] !== undefined;
        const isCurrent = ep.id === currentEpisodeId;
        // 收費劇 + 非 VIP + 超過頭 10 集 → 顯示 🔒（用家撳入去先真正判斷要唔要睇廣告）
        const locked = isPaidDrama && !isVip && ep.episode_number > FREE_EPISODE_LIMIT;
        return (
          <li key={ep.id}>
            <Link
              href={`/play/?episode=${ep.id}`}
              className={`${styles.item} ${isCurrent ? styles.current : ''}`}
            >
              <span className={styles.num}>{ep.episode_number}</span>
              <span className={styles.title}>{ep.title || `第 ${ep.episode_number} 集`}</span>
              <span className={styles.statusRow}>
                {isCurrent ? (
                  <span className={styles.now}>播放中</span>
                ) : watched ? (
                  <span className={styles.watched}>已看</span>
                ) : null}
                {locked && (
                  <span className={styles.lock} aria-label="需觀看廣告解鎖">
                    🔒
                  </span>
                )}
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
