"""爬蟲資料模型。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ShortDramaItem:
    """一部短劇的標準化元資料（跨來源通用）。"""

    source: str                     # 資料來源名稱，例如 "hongguo"
    series_id: str                  # 來源站嘅劇集 ID（用嚟追蹤/去重）
    title: str
    description: str | None = None
    cover_url: str | None = None
    tags: list[str] = field(default_factory=list)
    episode_count: int | None = None
    heat: int | None = None         # 熱度（萬）
    score: float | None = None      # 評分
    rank: int | None = None         # 排行榜名次
    is_completed: bool = False
    release_year: int | None = None
    detail_url: str | None = None

    @property
    def primary_tag(self) -> str | None:
        """主分類標籤：取第一隻 tag（來源通常將最闊嘅類型放最前）。"""
        for t in self.tags:
            t = t.strip()
            if t:
                return t
        return None
