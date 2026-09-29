"""紅果片 URL on-demand 重抓服務（短 cache，唔長存過期 CDN URL）。

背景：紅果 qznovelvod.com 嘅 signed MP4 URL 約莫 1 個鐘就過期（返 403）。
做法：
1. 開播時先用 ``player_path`` 入紅果 player 頁，由 SSR ld+json
   ``VideoObject.contentUrl`` 抽新簽名 URL（重用 ``HongguoCrawler.parse_player_video``）；
2. 用 in-memory dict 缓存約 25 分鐘（key = player_path），避免每集播都打紅果；
3. caller（``/episodes/{id}/stream``）再用 HEAD 驗證新 URL 真係 200 + ``video/`` +
   content-length > 1000 byte，合格先返畀前端。

全部用 sync ``httpx.Client``，因為 stream endpoint 係 sync。
"""
from __future__ import annotations

import logging
import time

import httpx

from scripts.crawler.hongguo import BASE_URL, HongguoCrawler  # type: ignore

log = logging.getLogger("services.hongguo_playback")

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# player_path -> (expires_at_unix, fresh_video_url)
_cache: dict[str, tuple[float, str]] = {}
CACHE_TTL_SEC = 25 * 60.0  # 約 25 分鐘


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=12.0,
        follow_redirects=True,
        headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"},
    )


def fetch_fresh_url(player_path: str | None) -> str | None:
    """入紅果 player 頁抽新簽名 contentUrl。

    - 用 in-memory cache（key = player_path）住約 25 分鐘，避免每集都打紅果；
    - 抽唔到 / 抓取失敗返 None。
    """
    if not player_path:
        return None

    cached = _cache.get(player_path)
    if cached and cached[0] > time.time():
        log.info("用 cache 嘅片 URL player_path=%s", player_path)
        return cached[1]

    url = player_path if player_path.startswith("http") else f"{BASE_URL}{player_path}"
    try:
        with _client() as cli:
            r = cli.get(url)
            r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        log.warning("player 頁抓取失敗 %s: %s", url, exc)
        return None

    video_url, _name = HongguoCrawler.parse_player_video(r.text)
    if not video_url:
        log.warning("player 頁抽唔到 contentUrl %s", player_path)
        return None

    _cache[player_path] = (time.time() + CACHE_TTL_SEC, video_url)
    return video_url


def head_video_ok(url: str | None) -> bool:
    """HEAD 驗證片 URL 係咪真係播到：200 + content-type 開頭 video/ + content-length > 1000 byte。"""
    if not url:
        return False
    try:
        with _client() as cli:
            r = cli.head(url, follow_redirects=True)
    except Exception as exc:  # noqa: BLE001
        log.warning("HEAD 失敗 %s: %s", url[:80], exc)
        return False

    if r.status_code != 200:
        return False
    ctype = r.headers.get("content-type", "")
    if not ctype.startswith("video/"):
        return False
    try:
        length = int(r.headers.get("content-length", "0") or 0)
    except ValueError:
        length = 0
    return length > 1000
