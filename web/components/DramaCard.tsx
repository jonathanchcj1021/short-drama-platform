'use client';

import Link from 'next/link';
import PosterPlaceholder from './PosterPlaceholder';
import { sourceLabel } from '@/lib/sources';
import type { DramaListItem } from '@/types';
import styles from './DramaCard.module.css';

interface Props {
  drama: DramaListItem;
}

export default function DramaCard({ drama }: Props) {
  const categoryLabel = drama.category?.name ?? drama.category_name ?? '未分類';
  const hasCover = Boolean(drama.cover_url);
  const from = sourceLabel(drama.source);

  // 誠實集數：用 DB 真實集數，唔好再用 metadata episode_count 誤導
  const realCount = drama.real_episode_count ?? 0;
  const showRealBadge = realCount > 0;
  const showMetaBadge = !showRealBadge && realCount === 0 && drama.episode_count != null;

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

      {/* 集數 badge（右上角）：真集數先用「N 集」；淨係 metadata 就講明未接片源 */}
      {showRealBadge && <span className={styles.badge}>{realCount} 集</span>}
      {showMetaBadge && <span className={styles.badgeMeta}>資料卡 · 未接片源</span>}

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
