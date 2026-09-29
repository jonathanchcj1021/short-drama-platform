"""一次性 backfill：將 DB 現有劇集同紅果 mapping 對返，並預先簽一次新片 URL。

做嘅嘢：
1. 抓紅果 4 個熱播榜 + 首頁劇卡，建立 劇名 -> series_id 對照；
2. UPDATE dramas.hongguo_series_id（按劇名 match）；
3. 對每部有 mapping 嘅劇，抓 detail 頁，UPDATE episodes.player_path（頭幾集公開）；
4. 順手入 player 頁拎一次新 signed URL，UPDATE episodes.video_url。

用法：
    DATABASE_URL=... .venv/bin/python -m scripts.backfill_hongguo_mapping
"""
from __future__ import annotations

import re
import time

import httpx
from sqlalchemy import select

from app.database import SessionLocal
from app.models.drama import Drama
from app.models.episode import Episode
from scripts.crawler.hongguo import (
    BASE_URL,
    RANK_LISTS,
    HongguoCrawler,
)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def _norm(t: str) -> str:
    """標題正規化：去空白同常見標點，提高 match 率。"""
    return re.sub(r"[\s:：,，！!？?·\-_「」『』《》()（）]", "", t or "")


def fetch(client: httpx.Client, url: str) -> str:
    r = client.get(url)
    r.raise_for_status()
    time.sleep(0.4)
    return r.text


def build_title_map(client: httpx.Client) -> dict[str, str]:
    """抓 4 個榜 + 首頁，返 正規化劇名 -> series_id。"""
    title_to_id: dict[str, str] = {}
    for key, url in RANK_LISTS.items():
        try:
            html = fetch(client, url)
            for it in HongguoCrawler._parse_rank(html):
                title_to_id.setdefault(_norm(it.title), it.series_id)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! 抓榜單 {key} 失敗: {exc}")
    try:
        html = fetch(client, f"{BASE_URL}/")
        for it in HongguoCrawler._parse_home(html):
            title_to_id.setdefault(_norm(it.title), it.series_id)
    except Exception as exc:  # noqa: BLE001
        print(f"  ! 抓首頁失敗: {exc}")
    return title_to_id


def main() -> None:
    db = SessionLocal()
    dramas = list(db.scalars(select(Drama).order_by(Drama.id)))
    print(f"DB 有 {len(dramas)} 部劇")
    crawler = HongguoCrawler(client=None)  # _parse_* 係純 html 函式，唔用到 client

    with httpx.Client(timeout=20.0, headers={"User-Agent": UA}) as client:
        title_to_id: dict[str, str] = {}
        for key, url in RANK_LISTS.items():
            try:
                html = fetch(client, url)
                for it in crawler._parse_rank(html):
                    title_to_id.setdefault(_norm(it.title), it.series_id)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! 抓榜單 {key} 失敗: {exc}")
        try:
            html = fetch(client, f"{BASE_URL}/")
            for it in crawler._parse_home(html):
                title_to_id.setdefault(_norm(it.title), it.series_id)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! 抓首頁失敗: {exc}")
        print(f"紅果側抽到 {len(title_to_id)} 個劇名")

        matched = 0
        for d in dramas:
            sid = title_to_id.get(_norm(d.title))
            if sid:
                d.hongguo_series_id = sid
                matched += 1
            else:
                print(f"  - 冇 match 到 series_id: id={d.id} {d.title}")
        db.commit()
        print(f"對到 {matched}/{len(dramas)} 部劇嘅 hongguo_series_id")

        # 逐部劇：detail 頁補 player_path + 新 signed URL
        refreshed = 0
        for d in dramas:
            if not d.hongguo_series_id:
                continue
            try:
                html = fetch(client, f"{BASE_URL}/detail?series_id={d.hongguo_series_id}")
            except Exception as exc:  # noqa: BLE001
                print(f"  ! detail 失敗 id={d.id}: {exc}")
                continue
            public = {e.episode_number: e.player_path for e in HongguoCrawler.parse_detail_episodes(html)}

            eps = list(db.scalars(select(Episode).where(Episode.drama_id == d.id)))
            for ep in eps:
                pp = public.get(ep.episode_number)
                if not pp:
                    continue
                ep.player_path = pp
                # 入 player 頁拎新 signed URL
                try:
                    pu = fetch(client, pp if pp.startswith("http") else f"{BASE_URL}{pp}")
                    new_url, _ = HongguoCrawler.parse_player_video(pu)
                except Exception as exc:  # noqa: BLE001
                    print(f"    ! player 失敗 ep{ep.episode_number}: {exc}")
                    new_url = None
                if new_url:
                    ep.video_url = new_url
                    refreshed += 1
            db.commit()
        print(f"刷新咗 {refreshed} 集嘅 player_path / video_url")

    db.close()
    print("backfill 完成。")


if __name__ == "__main__":
    main()
