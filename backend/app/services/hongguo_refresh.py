"""紅果 signed video URL 即時重簽服務。

背景：紅果 qznovelvod.com 嘅 signed MP4 URL 約莫 1 個鐘就會過期（返 403）。
本服務負責：
1. 用 Range GET（bytes=0-1）探一下舊 URL 仲生唔生；
2. 死咗就用 drama.hongguo_series_id + episode.player_path 重新入紅果 player 頁，
   由 SSR ld+json ``contentUrl`` 抽新 signed URL；
3. 新 URL 寫回 DB 並 cache 一段短時間（預設 5 分鐘），避免次次播片都入紅果。

全部用 sync ``httpx.Client``，因為 ``/episodes/{id}/stream`` 係 sync endpoint。
"""
from __future__ import annotations

import logging
import time

import httpx

from scripts.crawler.hongguo import (  # type: ignore
    BASE_URL,
    _CONTENT_URL_RE,
    _PUBLIC_EP_RE,
)

log = logging.getLogger("services.hongguo_refresh")

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# episode_id -> (expires_at_unix, fresh_url)
_url_cache: dict[int, tuple[float, str]] = {}
CACHE_TTL_SEC = 300.0

QZNOWEL_HOST = "qznovelvod.com"


def is_hongguo_signed_url(url: str | None) -> bool:
    return bool(url) and QZNOWEL_HOST in url


def is_placeholder_url(url: str | None) -> bool:
    return bool(url) and "placeholder-soon" in url


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=12.0,
        follow_redirects=True,
        headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"},
    )


def probe_url_alive(url: str) -> bool:
    """用 Range GET 探 URL 仲可唔可以拎到片。200/206 當生。"""
    try:
        with _client() as cli:
            r = cli.get(url, headers={"Range": "bytes=0-1"})
            return r.status_code in (200, 206)
    except Exception as exc:  # noqa: BLE001
        log.warning("probe 失敗 %s: %s", url[:80], exc)
        return False


def fetch_player_video_sync(player_path: str) -> str | None:
    """入 player 頁抽新 signed contentUrl。抽唔到返 None。"""
    if not player_path:
        return None
    url = player_path if player_path.startswith("http") else f"{BASE_URL}{player_path}"
    try:
        with _client() as cli:
            r = cli.get(url)
            r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        log.warning("player 頁抓取失敗 %s: %s", url, exc)
        return None
    m = _CONTENT_URL_RE.search(r.text)
    if not m:
        return None
    return m.group(1).replace("&amp;", "&")


def fetch_detail_episode_paths_sync(series_id: str) -> dict[int, str]:
    """入 detail 頁攞公開解鎖集嘅 player_path，返 {episode_number: player_path}。"""
    url = f"{BASE_URL}/detail?series_id={series_id}"
    try:
        with _client() as cli:
            r = cli.get(url)
            r.raise_for_status()
            html = r.text
    except Exception as exc:  # noqa: BLE001
        log.warning("detail 頁抓取失敗 series_id=%s: %s", series_id, exc)
        return {}
    out: dict[int, str] = {}
    for href, num in _PUBLIC_EP_RE.findall(html):
        out[int(num)] = href
    return out


def resolve_hongguo_url(
    *,
    episode_id: int,
    drama_series_id: str | None,
    episode_number: int,
    stored_player_path: str | None,
    old_url: str,
) -> tuple[str | None, str | None]:
    """為一集過期紅果片重簽新 URL。

    返 (new_url, player_path_used)。拎唔到就 (None, None)。
    成功嘅話 caller 負責 UPDATE DB。
    """
    cached = _url_cache.get(episode_id)
    if cached and cached[0] > time.time():
        log.info("使用 cache 嘅新 URL episode_id=%s", episode_id)
        return cached[1], stored_player_path

    if probe_url_alive(old_url):
        # 仲生，唔使重簽（順手入 cache）
        _url_cache[episode_id] = (time.time() + CACHE_TTL_SEC, old_url)
        return old_url, stored_player_path

    if not drama_series_id:
        log.warning("冇 hongguo_series_id，無法重簽 episode_id=%s", episode_id)
        return None, None

    player_path = stored_player_path
    if not player_path:
        paths = fetch_detail_episode_paths_sync(drama_series_id)
        player_path = paths.get(episode_number)
        if not player_path:
            log.warning(
                "detail 頁冇第 %s 集公開連結 series_id=%s", episode_number, drama_series_id
            )
            return None, None

    new_url = fetch_player_video_sync(player_path)
    if not new_url:
        log.warning("player 頁抽唔到 contentUrl %s", player_path)
        return None, None

    _url_cache[episode_id] = (time.time() + CACHE_TTL_SEC, new_url)
    return new_url, player_path
