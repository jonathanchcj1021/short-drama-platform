'use client';

import Link from 'next/link';
import type { Episode } from '@/types';
import styles from './EpisodeList.module.css';

interface Props {
  episodes: Episode[];
  /** 目前觀看到的 episodeId（用於標記已觀看） */
  currentEpisodeId?: number;
  /** 觀看進度對照表：episodeId -> positionSec */
  progressMap?: Record<number, number>;
}

export default function EpisodeList({ episodes, currentEpisodeId, progressMap = {} }: Props) {
  if (!episodes || episodes.length === 0) {
    return <p className={styles.empty}>尚無集數</p>;
  }

  return (
    <ul className={styles.list}>
      {episodes.map((ep) => {
        const watched = progressMap[ep.id] !== undefined;
        const isCurrent = ep.id === currentEpisodeId;
        return (
          <li key={ep.id}>
            <Link
              href={`/play/${ep.id}`}
              className={`${styles.item} ${isCurrent ? styles.current : ''}`}
            >
              <span className={styles.num}>第 {ep.episodeNumber} 集</span>
              <span className={styles.title}>{ep.title}</span>
              {watched && <span className={styles.watched}>已觀看</span>}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
