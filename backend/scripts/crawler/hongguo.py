"""紅果短劇（hongguoduanju.com）公開頁面爬蟲。

資料來源（只讀公開 HTML）：
- 首頁：https://hongguoduanju.com —— 熱播劇卡（劇名/封面/全 N 集/分類標籤）
- 熱播榜：https://hongguoduanju.com/rank/hot-drama —— 排名、熱度、評分、收藏/點讚、簡介

CSS class 名稱帶 CSS-Module hash 後綴，parser 用語義前綴（class*="pc-title-"）匹配。
"""
from __future__ import annotations

import asyncio
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

from scripts.crawler.items import ShortDramaItem

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

    async def crawl(self, limit: int = 20) -> list[ShortDramaItem]:
        """抓 4 個每日熱播榜＋首頁劇卡，合併後返回首 `limit` 部。

        排序：綜合榜（hot）順序優先，其後係真人劇/AI劇/漫劇榜，最後先係淨喺首頁出現嘅劇。
        """
        per_list = max(limit // len(RANK_LISTS), 5)
        all_items: list[ShortDramaItem] = []
        for key in RANK_LISTS:
            all_items.extend(await self.fetch_rank(limit=per_list, list_key=key))
        home_items = await self.fetch_home()
        merged = self.merge(all_items, home_items)
        return merged[:limit]
