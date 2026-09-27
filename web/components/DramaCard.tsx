'use client';

import Link from 'next/link';
import type { Drama } from '@/types';
import styles from './DramaCard.module.css';

interface Props {
  drama: Drama;
}

export default function DramaCard({ drama }: Props) {
  const categoryLabel = drama.category?.name ?? drama.category_name ?? '未分類';
  const hasCover = Boolean(drama.cover_url);

  return (
    <Link href={`/drama/?id=${drama.id}`} className={styles.card}>
      {hasCover ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={drama.cover_url} alt={drama.title} className={styles.cover} />
      ) : (
        <div className={styles.placeholder}>
          <span className={styles.placeholderTitle}>{drama.title}</span>
        </div>
      )}

      {/* 底部 scrim */}
      <div className={styles.scrim} />

      {/* 頂左分類 chip */}
      <span className={styles.chip}>{categoryLabel}</span>

      {/* 正中間 hover 播放鈕 */}
      <span className={styles.playBtn} aria-hidden>
        ▶
      </span>

      {/* 底部文字區 */}
      <div className={styles.info}>
        <h3 className={styles.title}>{drama.title}</h3>
        <div className={styles.meta}>
          <span className={styles.dot} />
          <span>{drama.episode_count != null ? `${drama.episode_count} 集` : '更新中'}</span>
        </div>
      </div>
    </Link>
  );
}
