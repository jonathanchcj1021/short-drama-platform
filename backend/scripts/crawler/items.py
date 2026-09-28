"""爬蟲資料模型。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScrapedEpisode:
    """單一集嘅資料。

    - ``episode_number``：集數（由 detail 頁格子讀出，由 1 開始）。
    - ``player_path``：公開 player 頁路徑（``/player/<series_id>`` 或
      ``/player/<series_id>/<item_id>``）。只有公開解鎖嘅集先有。
    - ``video_url``：由 player 頁 SSR ld+json ``VideoObject.contentUrl`` 抽出嘅
      **真實可播放片 URL**（紅果 VOD CDN signed MP4）。未抽到則為 None。
    - ``title``／``duration``：額外 metadata（可為 None）。
    """

    episode_number: int
    title: str | None = None
    player_path: str | None = None
    video_url: str | None = None
    duration: int | None = None


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
    episodes: list[ScrapedEpisode] = field(default_factory=list)  # 公開可播放嘅集

    @property
    def primary_tag(self) -> str | None:
        """主分類標籤：取第一隻 tag（來源通常將最闊嘅類型放最前）。"""
        for t in self.tags:
            t = t.strip()
            if t:
                return t
        return None
