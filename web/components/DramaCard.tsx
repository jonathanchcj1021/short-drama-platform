'use client';

import Link from 'next/link';
import type { Drama } from '@/types';
import styles from './DramaCard.module.css';

interface Props {
  drama: Drama;
}

export default function DramaCard({ drama }: Props) {
  // 若後端未給封面，使用 SVG placeholder
  const cover =
    drama.coverUrl ||
    `data:image/svg+xml;utf8,${encodeURIComponent(
      `<svg xmlns='http://www.w3.org/2000/svg' width='300' height='400'><rect width='100%' height='100%' fill='#3a3a44'/><text x='50%' y='50%' fill='#888' font-size='20' text-anchor='middle' dominant-baseline='middle'>${drama.title}</text></svg>`,
    )}`;

  return (
    <Link href={`/drama/?id=${drama.id}`} className={styles.card}>
      <div className={styles.coverWrap}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={cover} alt={drama.title} className={styles.cover} />
        <span className={styles.badge}>{drama.episodeCount} 集</span>
      </div>
      <div className={styles.body}>
        <h3 className={styles.title}>{drama.title}</h3>
        <p className={styles.category}>{drama.category?.name ?? drama.categoryName ?? '未分類'}</p>
      </div>
    </Link>
  );
}
