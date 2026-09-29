"""番茄短劇（fanqienovel.com）公開頁面爬蟲 —— 實地探查後結論：暫時無公開短劇網頁可爬。

【實地探查紀錄（2026-09-29，curl + httpx）】
番茄小說官網 fanqienovel.com 本質上係「小說」網站，唔係短劇網站：
  - 首頁 <title> = 「小说,番茄小说网_好看的小说尽在番茄小说官网」
  - /rank     <title> = 「小说排行榜_番茄小说官网」（全部係小說分類榜：都市日常、
                東方仙俠、宮鬥宅鬥、種田……冇任何「短劇」分類 tab）
  - /library <title> = 「书库_番茄小说官网」（小說書庫）
  - 首頁入面出現嘅「短剧」字樣，只係小說 abstract 寫「同名短剧已上线」嘅改編廣告，
    唔係獨立短劇頻道。
  - /shortplay、/duanju、/category 全部 404；drama./duanju./shortplay. 子域名 DNS 唔存在。
  - fanqieduanju.com / .cn / .net 呢類獨立短劇域名全部 DNS 唔存在（連唔上）。

【點解唔爬】
ByteDance 旗下真正嘅短劇網頁入口其實係「紅果短劇」hongguoduanju.com——呢個已經由
hongguo.py 覆蓋，唔使重複做。「番茄短劇」只係 番茄小說 App 入面嘅一個頻道 tab，
並無對外嘅公開網頁排行榜 / 片單 / 播放頁。網上聲稱「番茄榜單」嘅第三方站（例如
ghtic.com、tcweekly.com 等）唔係 ByteDance 官方網域，版權來源唔清，唔應該爬。

【本檔案嘅角色】
照 hongguo.py 嘅介面實作一個 ``FanqieCrawler``，但 ``crawl()`` 會真係去抓一次
fanqienovel.com 首頁確認現況，然後**誠實地回傳空 list**（唔造任何假劇名 / 假片 URL）。
將來若官方開放短劇網頁頻道，先至係呢個檔案落實 parser 嘅地方。
"""
from __future__ import annotations

import asyncio
import logging
import re

import httpx

from scripts.crawler.items import ShortDramaItem

log = logging.getLogger("crawler.fanqie")

BASE_URL = "https://fanqienovel.com"
HOME_URL = f"{BASE_URL}/"
RANK_URL = f"{BASE_URL}/rank"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
}

_TITLE_RE = re.compile(r"<title>([^<]*)</title>")


class FanqieCrawler:
    """番茄短劇公開頁面爬蟲。

    目前狀態：**無公開短劇網頁可爬**。``crawl()`` 會做一次輕量探查（抓首頁 + 排行榜頁），
    確認佢哋仲係小說站，然後回傳空 list。呢個類別存在嘅目的：
      1. 令 organizer 可以照樣註冊 ``name="fanqie"``，唔會 import 爆；
      2. 將「點解 fanqie 匯入到 0 套劇」嘅原因寫死喺 log，唔會當成 silent failure；
      3. 將來官方一旦開放短劇網頁頻道，parser 有現成位置加。
    """

    name = "fanqie"

    def __init__(self, client: httpx.AsyncClient, request_delay: float = 0.6):
        self.client = client
        self.request_delay = request_delay

    async def _get(self, url: str) -> str:
        resp = await self.client.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        await asyncio.sleep(self.request_delay)  # 尊重速率限制
        return resp.text

    @staticmethod
    def _page_title(html: str) -> str | None:
        m = _TITLE_RE.search(html)
        return m.group(1).strip() if m else None

    async def probe(self) -> dict:
        """實際抓一次首頁 + 排行榜頁，回傳探查結果（供 smoke test 同 log 用）。

        回傳 dict 例：``{"home_title": "...", "rank_title": "...", "is_novel_site": True}``。
        """
        home_html = await self._get(HOME_URL)
        rank_html = await self._get(RANK_URL)
        home_title = self._page_title(home_html)
        rank_title = self._page_title(rank_html)
        # 番茄網站無論首頁定排行榜，title 一定係「小说/書庫」字樣；
        # 短劇頻道如果真係出現，title 唔會再係小說榜。
        is_novel_site = bool(
            home_title and ("小说" in home_title or "番茄小说" in home_title)
        )
        return {
            "home_title": home_title,
            "rank_title": rank_title,
            "is_novel_site": is_novel_site,
        }

    async def crawl(
        self,
        limit: int = 20,
        with_episodes: bool = False,
    ) -> list[ShortDramaItem]:
        """探查 fanqienovel.com 係咪真係開咗短劇網頁頻道。

        依現地探查：兩頁都係小說站，冇短劇排行榜 / 片單，所以**回傳空 list**。
        唔會捏造任何 ``ShortDramaItem``，更加唔會填 ``episodes[].video_url``。
        """
        try:
            info = await self.probe()
        except Exception as exc:  # noqa: BLE001
            # 網絡 / 反爬問題都唔會 raise 爆 organizer，只係回傳空 list。
            log.warning("fanqie 探查失敗（可能被擋）: %s", exc)
            return []

        log.info(
            "fanqie 探查結果 home_title=%r rank_title=%r → 小說站=%s，無公開短劇頻道，回傳 0 套劇",
            info["home_title"],
            info["rank_title"],
            info["is_novel_site"],
        )
        return []
