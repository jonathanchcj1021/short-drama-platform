"""抖音短劇（douyin.com / iesdouyin.com）公開網頁爬蟲 —— 實地探查後結論：App / 登入牆後，無公開可爬片單。

【實地探查紀錄（2026-09-29，curl）】
  - https://www.douyin.com/ 同 https://www.douyin.com/search/短剧 回傳**同一個 72914 bytes
    嘅 SPA 空殼**：冇 <title>、冇「短剧」字樣、冇 RENDER_DATA / __pace_f / aweme 資料。
    即係所有內容都係前端 JS 用 XHR 去拎，唔係 SSR。
  - 抖音嘅 XHR API 全部要 ``a_bogus`` 簽名參數（反爬），呢度**唔會嘗試繞過**。
  - robots.txt（www.douyin.com/robots.txt）明確 Disallow：
      * /follow、*general_search*、*enter_from=*、*vid=*
      對 Baiduspider 仲額外 Disallow /search/、/video/、/note/、/zhuanti/、/topic/。
    → 連搜尋頁同影片頁對一般爬蟲都係唔畀抓。
  - 移動分享站 iesdouyin.com 根目錄直接 301 去 www.douyin.com（同一個空殼）；
    /drama、/share/drama 都係 404。
  - 個別分享影片頁 iesdouyin.com/share/video/<id> 雖然 200，但載入 ByteDance
    secsdk（secsdk.umd.js）做 captcha / verify，SSR HTML 入面**冇 ld+json VideoObject、
    冇 contentUrl、冇 series 資訊**。
  - 殘存嘅舊 API iesdouyin.com/web/api/v2/hotsearch/billboard/word/ 雖然 200，但佢回傳嘅
    係「通用熱搜詞榜」（例如「中國女足 vs 朝鮮女足」），**唔係短劇片單**，對本聚合平台無用。

【點解唔爬】
抖音短劇內容本質上係：(a) App 內嘅「短劇」頻道 tab；(b) 劇方帳號發嘅單條宣傳短片。
網頁版既冇 SSR 片單 / 排行榜，XHR 又要 a_bogus 簽名（屬於要繞過反爬先拎到，違反約束），
robots 亦明確唔畀抓 search/video。ByteDance 真正開放網頁短劇播放嘅入口仍然係
紅果短劇 hongguoduanju.com（已由 hongguo.py 覆蓋）。

【本檔案嘅角色】
照 hongguo.py 介面實作 ``DouyinCrawler``，但 ``crawl()`` 真係抓一次抖音首頁空殼確認現況，
然後**誠實地回傳空 list**（唔造假劇名 / 假片 URL，更加唔會生成 a_bogus）。
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from scripts.crawler.items import ShortDramaItem

log = logging.getLogger("crawler.douyin")

HOME_URL = "https://www.douyin.com/"
# 注意：robots Disallow *general_search*，呢度只係探查空殼大小，**唔會**真係去 parse 搜尋結果。
SEARCH_PROBE_URL = "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
}


class DouyinCrawler:
    """抖音短劇公開網頁爬蟲。

    目前狀態：**App / 簽名牆後，無公開 SSR 片單可爬**。``crawl()`` 做一次輕量探查確認
    抖音網頁仲係 SPA 空殼，然後回傳空 list。類別存在目的同 FanqieCrawler：
    令 organizer 可註冊 ``name="douyin"``、將空白原因寫入 log、將來若開放網頁片單先落 parser。
    """

    name = "douyin"

    def __init__(self, client: httpx.AsyncClient, request_delay: float = 0.6):
        self.client = client
        self.request_delay = request_delay

    async def _get(self, url: str) -> str:
        resp = await self.client.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        await asyncio.sleep(self.request_delay)  # 尊重速率限制
        return resp.text

    async def probe(self) -> dict:
        """實際抓一次首頁空殼，回傳 ``{"shell_bytes": N, "has_ssr_drama": bool}``。"""
        home_html = await self._get(HOME_URL)
        # 如果係真 SSR 片單，HTML 入面一定有「短剧」字樣 / 劇卡 / aweme id。
        has_ssr_drama = ("短剧" in home_html) or ("aweme" in home_html)
        return {
            "shell_bytes": len(home_html),
            "has_ssr_drama": has_ssr_drama,
        }

    async def crawl(
        self,
        limit: int = 20,
        with_episodes: bool = False,
    ) -> list[ShortDramaItem]:
        """探查抖音網頁有冇 SSR 短劇片單。

        依現地探查：douyin.com 係 SPA 空殼，內容要 a_bogus 簽名先拎到（唔繞），
        robots 亦 Disallow search/video。所以**回傳空 list**，唔捏造任何資料。
        """
        try:
            info = await self.probe()
        except Exception as exc:  # noqa: BLE001
            log.warning("douyin 探查失敗（可能被擋 / captcha）: %s", exc)
            return []

        log.info(
            "douyin 探查結果 shell_bytes=%d has_ssr_drama=%s → SPA+a_bogus 牆，無公開片單，回傳 0 套劇",
            info["shell_bytes"],
            info["has_ssr_drama"],
        )
        return []
