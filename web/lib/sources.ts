/** 來源平台代碼 → 繁體中文名稱。日後接入新 source 喺度加就得。 */
const SOURCE_LABELS: Record<string, string> = {
  hongguo: '紅果短劇',
};

/** 將後端 source 代碼轉成顯示名；冇 source 或未知代碼就適當回退。 */
export function sourceLabel(source?: string | null): string | null {
  if (!source) return null;
  return SOURCE_LABELS[source] ?? source;
}
