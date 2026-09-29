'use client';

import Link from 'next/link';
import PosterPlaceholder from './PosterPlaceholder';
import { sourceLabel } from '@/lib/sources';
import type { Drama } from '@/types';
import styles from './DramaCard.module.css';

interface Props {
  drama: Drama;
}

export default function DramaCard({ drama }: Props) {
  const categoryLabel = drama.category?.name ?? drama.category_name ?? '未分類';
  const hasCover = Boolean(drama.cover_url);
  const from = sourceLabel(drama.source);

  return (
    <Link href={`/drama/?id=${drama.id}`} className={styles.card}>
      {hasCover ? (
        <>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={drama.cover_url} alt={drama.title} className={styles.cover} loading="lazy" />
          <div className={styles.scrim} />
        </>
      ) : (
        <PosterPlaceholder title={drama.title} className={styles.cover} />
      )}

      {/* 頂左分類 chip */}
      <span className={styles.chip}>{categoryLabel}</span>

      {/* 集數 badge（右上角） */}
      {drama.episode_count != null && (
        <span className={styles.badge}>{drama.episode_count} 集</span>
      )}

      {/* 正中間 hover 播放鈕 */}
      <span className={styles.playBtn} aria-hidden>
        ▶
      </span>

      {/* 底部劇名 */}
      <div className={styles.info}>
        {from && <span className={styles.sourcePill}>來自：{from}</span>}
        <h3 className={styles.title}>{drama.title}</h3>
      </div>
    </Link>
  );
}
