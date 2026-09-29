"""優酷短劇（youku.com）公開搜尋結果頁爬蟲。

資料來源（只讀公開 SSR HTML，唔繞 DRM／VIP／登入）：
- 優酷將短劇目錄以「搜尋結果」形式 SSR 嵌入 ``window.__INITIAL_DATA__`` JSON：
  https://so.youku.com/search/q_<URL編關鍵字>
- 例如 ``好看的短剧``、``2025短剧`` 等關鍵字頁，每頁約 40+ 部短劇卡片。

點解只做 metadata-only：
- 優酷正片播放頁（``v.youku.com/v_show/...``）全部上 DRM／VIP／登入牆，
  server-side curl 拎唔到任何可播放片 URL，所以 ``episodes`` 永遠留空，唔造假。
- 卡片入面已經有：劇名、封面、集數（「劇・24集全」）、獨播／VIP 角標、
  年份、一句話簡介、``showId``（穩定劇集 ID）。

注意：
- 優酷係反爬較強嘅站，``request_delay`` 預設 >= 0.6s，用瀏覽器 UA。
- 卡片 JSON 結構由 ``window.__INITIAL_DATA__`` 直接 parse，唔靠 CSS class。
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Iterable

import httpx

from scripts.crawler.items import ShortDramaItem

log = logging.getLogger("crawler.youku")

BASE_URL = "https://so.youku.com"

# 用幾個公開關鍵字頁湊短劇目錄（優酷冇獨立短劇榜 SSR 頁，搜尋結果即目錄）。
# 每頁 server-side 都會 embed 完整卡片 JSON。
SEARCH_KEYWORDS: list[str] = [
    "好看的短剧",
    "2025短剧",
    "最新短剧",
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
}

# 「劇・24集全」「更新至08集」→ 抽集數
_EP_NUM_RE = re.compile(r"(\d+)\s*集")
# SSR JSON 邊界：window.__INITIAL_DATA__ = {...}; 之後係 window.__ENV__
_INITIAL_START = re.compile(r"window\.__INITIAL_DATA__\s*=\s*")
_INITIAL_END = "window.__ENV__"


def _to_int(text: str | None) -> int | None:
    if not text:
        return None
    m = _EP_NUM_RE.search(text)
    return int(m.group(1)) if m else None


def _https(url: str | None) -> str | None:
    """優酷封面好多係 http://r?.ykimg.com，統一升做 https。"""
    if not url:
        return None
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url


def _extract_initial_data(html: str) -> dict[str, Any] | None:
    """由 SSR HTML 抽 ``window.__INITIAL_DATA__`` JSON。

    抽唔到（例如被反爬改咗殼）就回傳 None，由 caller 決定降級。
    """
    m = _INITIAL_START.search(html)
    if not m:
        return None
    start = m.end()
    end = html.find(_INITIAL_END, start)
    blob = html[start:end].strip()
    if blob.endswith(";"):
        blob = blob[:-1]
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        log.warning("youku __INITIAL_DATA__ JSON parse 失敗")
        return None


def _iter_show_cards(node: Any) -> Iterable[dict[str, Any]]:
    """遞迴走 JSON，搵所有「短劇卡片」dict（同時有 tempTitle + showId）。"""
    if isinstance(node, dict):
        if "tempTitle" in node and "showId" in node:
            yield node
            return  # 卡片入面唔再嵌套子卡片
        for v in node.values():
            yield from _iter_show_cards(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_show_cards(v)


class YoukuCrawler:
    """優酷短劇公開搜尋結果爬蟲（metadata-only）。"""

    name = "youku"

    def __init__(self, client: httpx.AsyncClient, request_delay: float = 0.6):
        self.client = client
        self.request_delay = request_delay

    async def _get(self, url: str) -> str:
        resp = await self.client.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        await asyncio.sleep(self.request_delay)
        return resp.text

    # ---------- 單頁 parse ----------

    def parse_search_page(self, html: str) -> list[ShortDramaItem]:
        data = _extract_initial_data(html)
        if data is None:
            return []

        items: list[ShortDramaItem] = []
        seen: set[str] = set()
        for rank, card in enumerate(_iter_show_cards(data), start=1):
            show_id = card.get("showId") or card.get("realShowId")
            title = (
                (card.get("titleDTO") or {}).get("displayName")
                or card.get("tempTitle")
            )
            if not show_id or not title:
                continue
            if show_id in seen:
                continue
            # 只收「短劇」類別（搜「劇」會混入長劇）
            cats = card.get("cats") or ""
            if "短剧" not in cats and "短劇" not in cats:
                continue
            seen.add(show_id)

            poster = card.get("posterDTO") or {}
            left_bottom = (poster.get("leftBottomText") or {}).get("title", "")
            episode_count = _to_int(left_bottom)

            corner = poster.get("iconCorner") or {}
            corner_text = corner.get("tagText")
            tags = ["短剧"]
            if corner_text:
                tags.append(corner_text)  # 例：獨播、VIP

            cover = (
                poster.get("vThumbUrl")
                or card.get("sourceImg")
                or card.get("thumbUrl")
            )

            year_raw = card.get("releaseDate")
            try:
                release_year = int(year_raw) if year_raw else None
            except (TypeError, ValueError):
                release_year = None

            items.append(
                ShortDramaItem(
                    source=self.name,
                    series_id=show_id,
                    title=title,
                    description=card.get("subtitle"),
                    cover_url=_https(cover),
                    tags=tags,
                    episode_count=episode_count,
                    rank=rank,
                    is_completed=card.get("completed") == 1,
                    release_year=release_year,
                    detail_url=f"https://www.youku.com/play/showid_{show_id}.html",
                )
            )
        return items

    async def fetch_keyword(self, keyword: str) -> list[ShortDramaItem]:
        from urllib.parse import quote

        url = f"{BASE_URL}/search/q_{quote(keyword)}"
        html = await self._get(url)
        return self.parse_search_page(html)

    # ---------- 主入口 ----------

    async def crawl(
        self,
        limit: int = 20,
        with_episodes: bool = False,
    ) -> list[ShortDramaItem]:
        """抓幾個短劇關鍵字搜尋頁，合併去重後返回首 ``limit`` 部。

        ``with_episodes`` 參數保留介面一致：優酷正片全部 DRM／VIP，
        攞唔到公開可播放片 URL，所以無論點都唔填 ``episodes``（留空）。
        """
        merged: list[ShortDramaItem] = []
        seen: set[str] = set()
        for kw in SEARCH_KEYWORDS:
            try:
                page_items = await self.fetch_keyword(kw)
            except Exception as exc:  # noqa: BLE001
                log.warning("優酷關鍵字頁抓取失敗 %s: %s", kw, exc)
                continue
            for it in page_items:
                if it.series_id in seen:
                    continue
                seen.add(it.series_id)
                merged.append(it)
            if len(merged) >= limit:
                break

        # 排序：保留首次出現次序（即熱門關鍵字優先），rank 欄位只係頁內名次
        return merged[:limit]
