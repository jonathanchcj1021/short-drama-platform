interface Props {
  title: string;
  className?: string;
}

/**
 * 由劇名 hash 揀一個深色夢幻漸層，配柔光同播放 watermark，
 * 取代死灰色 placeholder。純漸層底，標題由卡片底部 overlay 統一處理。
 */
const PALETTES: Array<[string, string, string]> = [
  // 頂色, 中間色, 強光點
  ['#2b1055', '#7597de', '#ff6ec4'],
  ['#0f2027', '#2c5364', '#43cea2'],
  ['#42275a', '#734b6d', '#f5576c'],
  ['#3a1c71', '#d76d7a', '#ffb199'],
  ['#1a2980', '#26d0ce', '#a8ff78'],
  ['#41295a', '#2f0743', '#f857a6'],
  ['#232526', '#414345', '#ff512f'],
  ['#141e30', '#243b55', '#5ee7df'],
];

function hashString(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h << 5) - h + s.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

export default function PosterPlaceholder({ title, className }: Props) {
  const [c1, c2, glow] = PALETTES[hashString(title) % PALETTES.length];
  const style: React.CSSProperties = {
    background: `linear-gradient(160deg, ${c1} 0%, ${c2} 100%)`,
  };

  return (
    <div className={className} style={style} aria-hidden>
      {/* 柔光點綴 */}
      <span
        className="ppGlow"
        style={{ background: `radial-gradient(circle at 70% 18%, ${glow}66, transparent 62%)` }}
      />
      <span className="ppWatermark">▶</span>
    </div>
  );
}
