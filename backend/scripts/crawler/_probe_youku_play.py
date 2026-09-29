"""STEP7: 喺 v_show 頁 HTML 入面搵其他 vid（episode list 線索）+ 確認 paywall 狀態。"""
from __future__ import annotations

import asyncio
import re

import httpx

from scripts.crawler.youku import DEFAULT_HEADERS

VID = "XNjUyOTU5MzQxNg=="


def log(msg: str) -> None:
    print(msg, flush=True)


async def main() -> None:
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        url = f"https://v.youku.com/v_show/id_{VID}.html"
        r = await client.get(url, headers={**DEFAULT_HEADERS, "Referer": "https://so.youku.com/"})
        t = r.text
        # 搵所有 id_XXX== 形式 vid
        vids = set(re.findall(r"id_([A-Za-z0-9+/=]{10,}={0,3})", t))
        log(f"頁面入面出現嘅 vid 候選: {len(vids)} 個")
        for v in list(vids)[:15]:
            log(f"    {v}")
        # paywall / vip 狀態字樣
        for kw in ["需要会员", "开通会员", "VIP", "付费", "试看", "preview", "encryptR", "drmLicense", "msv"]:
            cnt = t.count(kw)
            if cnt:
                log(f"  字樣 {kw!r} 出現 {cnt} 次")
        # 結尾係咪有反爬殼
        for kw in ["punish", "验证码", "滑块", "___p__", "acw_sc__v2", "ycData"]:
            if kw in t:
                log(f"  反爬殼字樣: {kw}")


if __name__ == "__main__":
    asyncio.run(main())
