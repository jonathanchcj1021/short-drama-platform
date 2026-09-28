"""紅果短劇（hongguoduanju.com）公開頁面爬蟲。

資料來源（只讀公開 HTML）：
- 首頁：https://hongguoduanju.com —— 熱播劇卡（劇名/封面/全 N 集/分類標籤）
- 熱播榜：https://hongguoduanju.com/rank/hot-drama —— 排名、熱度、評分、收藏/點讚、簡介

CSS class 名稱帶 CSS-Module hash 後綴，parser 用語義前綴（class*="pc-title-"）匹配。
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

from scripts.crawler.items import ScrapedEpisode, ShortDramaItem

log = logging.getLogger("crawler.hongguo")

BASE_URL = "https://hongguoduanju.com"
RANK_URL = f"{BASE_URL}/rank/hot-drama"
HOME_URL = BASE_URL

# 每日更新嘅 4 個熱播榜（綜合/真人劇/AI劇/漫劇）
RANK_LISTS: dict[str, str] = {
    "hot": f"{BASE_URL}/rank/hot-drama",
    "real": f"{BASE_URL}/rank/hot-real-drama",
    "comic": f"{BASE_URL}/rank/hot-comic-drama",
    "ai": f"{BASE_URL}/rank/hot-ai-drama",
}

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
}

_SERIES_ID_RE = re.compile(r"series_id=(\d+)")
_NUM_RE = re.compile(r"(\d+(?:\.\d+)?)")
_EPISODE_RE = re.compile(r"(\d+)\s*集")

# detail 頁入面「公開解鎖」嘅集格：<a href="/player/..."><div ...>N</div></a>
# 其餘鎖住嘅集只係普通 <div>，冇 href，即係要登入 / App 先解鎖。
_PUBLIC_EP_RE = re.compile(
    r'<a href="(/player/[^"]+)"[^>]*>\s*'
    r'<div class="pc-episode-cell-text[^"]*">(\d+)</div>'
)
# player 頁 SSR ld+json VideoObject：真實片 URL 就係呢度。
_CONTENT_URL_RE = re.compile(r'"contentUrl":"([^"]+)"')
_VIDEO_NAME_RE = re.compile(r'"@type":"VideoObject"[^}]*?"name":"([^"]+)"')


def _extract_series_id(href: str | None) -> str | None:
    if not href:
        return None
    m = _SERIES_ID_RE.search(href)
    return m.group(1) if m else None


def _to_int(text: str | None) -> int | None:
    if not text:
        return None
    m = _NUM_RE.search(text)
    return int(m.group(1)) if m else None


def _to_float(text: str | None) -> float | None:
    if not text:
        return None
    m = _NUM_RE.search(text)
    return float(m.group(1)) if m else None


class HongguoCrawler:
    """紅果短劇公開頁面爬蟲。"""

    name = "hongguo"

    def __init__(self, client: httpx.AsyncClient, request_delay: float = 0.6):
        self.client = client
        self.request_delay = request_delay

    async def _get(self, url: str) -> str:
        resp = await self.client.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        await asyncio.sleep(self.request_delay)
        return resp.text

    # ---------- 熱播榜 ----------

    def _parse_rank(self, html: str) -> list[ShortDramaItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[ShortDramaItem] = []
        for li in soup.select("li[class*='pc-list-item-']"):
            if not isinstance(li, Tag):
                continue
            cover_link = li.select_one("a[class*='pc-cover-link-']")
            series_id = _extract_series_id(cover_link.get("href") if cover_link else None)
            title_el = li.select_one("h2[class*='pc-title-']")
            title = title_el.get_text(strip=True) if title_el else None
            if not title or not series_id:
                continue

            cover_img = li.select_one("img[class*='pc-cover-']")
            cover_url = cover_img.get("src") if cover_img else None

            rank_el = li.select_one("span[class*='pc-badge-number-']")
            rank = _to_int(rank_el.get_text(strip=True)) if rank_el else None

            heat_el = li.select_one("p[class*='pc-metrics-']")
            heat = _to_int(heat_el.get_text()) if heat_el else None

            tags: list[str] = []
            for span in li.select("p[class*='pc-categories-'] span"):
                t = span.get_text(strip=True)
                if t:
                    tags.append(t)

            score: float | None = None
            is_new = False
            for li_eng in li.select("ul[class*='pc-engagement-'] li"):
                text = li_eng.get_text(strip=True)
                if not text:
                    continue
                if "评分" in text:
                    score = _to_float(text)
                elif text == "新剧":
                    is_new = True

            desc_el = li.select_one("p[class*='pc-description-']")
            description = desc_el.get_text(strip=True) if desc_el else None

            items.append(
                ShortDramaItem(
                    source=self.name,
                    series_id=series_id,
                    title=title,
                    description=description,
                    cover_url=cover_url,
                    tags=tags,
                    heat=heat,
                    score=score,
                    rank=rank,
                    detail_url=f"{BASE_URL}/detail?series_id={series_id}",
                    is_completed=False,
                )
            )
        return items

    async def fetch_rank(self, limit: int = 20, list_key: str = "hot") -> list[ShortDramaItem]:
        url = RANK_LISTS.get(list_key, RANK_LISTS["hot"])
        html = await self._get(url)
        items = self._parse_rank(html)
        return items[:limit]

    # ---------- 首頁熱播劇卡 ----------

    def _parse_home(self, html: str) -> list[ShortDramaItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[ShortDramaItem] = []
        seen: set[str] = set()
        for card in soup.select("a[class*='pc-scatter-card-']"):
            if not isinstance(card, Tag):
                continue
            series_id = _extract_series_id(card.get("href"))
            title_el = card.select_one("p[class*='pc-scatter-card-title-']")
            title = title_el.get_text(strip=True) if title_el else None
            if not title or not series_id or series_id in seen:
                continue
            seen.add(series_id)

            img = card.select_one("img")
            cover_url = img.get("src") if img else None

            ep_el = card.select_one("span[class*='pc-scatter-episode-']")
            episode_count = _to_int(ep_el.get_text()) if ep_el else None

            tags: list[str] = []
            for span in card.select("div[class*='pc-scatter-tags-'] span"):
                t = span.get_text(strip=True)
                if t:
                    tags.append(t)

            items.append(
                ShortDramaItem(
                    source=self.name,
                    series_id=series_id,
                    title=title,
                    cover_url=cover_url,
                    tags=tags,
                    episode_count=episode_count,
                    detail_url=f"{BASE_URL}/detail?series_id={series_id}",
                )
            )
        return items

    async def fetch_home(self) -> list[ShortDramaItem]:
        html = await self._get(HOME_URL)
        return self._parse_home(html)

    # ---------- detail 頁：公開集數列表 ----------

    @staticmethod
    def parse_detail_episodes(html: str) -> list[ScrapedEpisode]:
        """由 detail 頁 SSR HTML 抽出「公開解鎖」嘅集。

        紅果將絕大部分集數鎖住（普通 <div>，冇 href，要登入／App 先解鎖），
        只有頭幾集係 <a href="/player/..."> 公開連結。呢度只抽得到公開嗰幾集。
        """
        episodes: list[ScrapedEpisode] = []
        seen: set[int] = set()
        for href, num in _PUBLIC_EP_RE.findall(html):
            n = int(num)
            if n in seen:
                continue
            seen.add(n)
            episodes.append(
                ScrapedEpisode(episode_number=n, player_path=href, title=f"第{n}集")
            )
        episodes.sort(key=lambda e: e.episode_number)
        return episodes

    async def fetch_detail_episodes(self, series_id: str) -> list[ScrapedEpisode]:
        url = f"{BASE_URL}/detail?series_id={series_id}"
        html = await self._get(url)
        return self.parse_detail_episodes(html)

    # ---------- player 頁：真實片 URL ----------

    @staticmethod
    def parse_player_video(html: str) -> tuple[str | None, str | None]:
        """由 player 頁 SSR ld+json ``VideoObject.contentUrl`` 抽真實片 URL。

        回傳 (video_url, video_name)。抽唔到就 (None, None)。
        """
        m = _CONTENT_URL_RE.search(html)
        if not m:
            return None, None
        video_url = m.group(1).replace("&amp;", "&")
        nm = _VIDEO_NAME_RE.search(html)
        video_name = nm.group(1) if nm else None
        return video_url, video_name

    async def fetch_player_video(self, player_path: str) -> tuple[str | None, str | None]:
        url = player_path if player_path.startswith("http") else f"{BASE_URL}{player_path}"
        html = await self._get(url)
        return self.parse_player_video(html)

    async def enrich_item_with_episodes(
        self, item: ShortDramaItem, max_episodes: int = 3
    ) -> ShortDramaItem:
        """入 detail 頁拎公開集，再逐集入 player 頁抽真實 video_url。

        任何一步失敗都唔會 raise（回傳已抽到嘅部份），保證 metadata 匯入唔中斷。
        """
        try:
            public_eps = await self.fetch_detail_episodes(item.series_id)
        except Exception as exc:  # noqa: BLE001
            log.warning("detail 頁抓取失敗 series_id=%s: %s", item.series_id, exc)
            return item

        for ep in public_eps[:max_episodes]:
            try:
                video_url, vname = await self.fetch_player_video(ep.player_path or "")
            except Exception as exc:  # noqa: BLE001
                log.warning("player 頁抓取失敗 %s: %s", ep.player_path, exc)
                continue
            if video_url:
                ep.video_url = video_url
                if vname:
                    ep.title = vname
                item.episodes.append(ep)
        return item

    # ---------- 合併 ----------

    @staticmethod
    def merge(rank_items: list[ShortDramaItem], home_items: list[ShortDramaItem]) -> list[ShortDramaItem]:
        """合併熱播榜＋首頁劇卡：以 series_id 為鍵，首頁補上集數，榜單補上簡介/熱度/評分。

        排序：榜單次序為先（rank 順序），其後係淨喺首頁出現嘅劇。
        """
        home_by_id = {i.series_id: i for i in home_items}
        merged: list[ShortDramaItem] = []
        seen: set[str] = set()

        for item in rank_items:
            h = home_by_id.get(item.series_id)
            if h and item.episode_count is None:
                item.episode_count = h.episode_count
            if h and not item.tags and h.tags:
                item.tags = h.tags
            merged.append(item)
            seen.add(item.series_id)

        for item in home_items:
            if item.series_id not in seen:
                merged.append(item)
        return merged

    async def crawl(
        self,
        limit: int = 20,
        with_episodes: bool = False,
        max_episodes_per_drama: int = 3,
    ) -> list[ShortDramaItem]:
        """抓 4 個每日熱播榜＋首頁劇卡，合併後返回首 `limit` 部。

        排序：綜合榜（hot）順序優先，其後係真人劇/AI劇/漫劇榜，最後先係淨喺首頁出現嘅劇。

        ``with_episodes=True`` 時，逐部劇入 detail 頁拎公開集、再入 player 頁抽真片 URL
        （每部最多 ``max_episodes_per_drama`` 集，因為紅果頭幾集先公開）。
        """
        per_list = max(limit // len(RANK_LISTS), 5)
        all_items: list[ShortDramaItem] = []
        for key in RANK_LISTS:
            all_items.extend(await self.fetch_rank(limit=per_list, list_key=key))
        home_items = await self.fetch_home()
        merged = self.merge(all_items, home_items)
        merged = merged[:limit]

        if with_episodes:
            enriched: list[ShortDramaItem] = []
            for item in merged:
                enriched.append(
                    await self.enrich_item_with_episodes(
                        item, max_episodes=max_episodes_per_drama
                    )
                )
            merged = enriched
        return merged
