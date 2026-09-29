"""短劇爬蟲 CLI + 匯入平台資料庫。

用法（喺 backend/ 目錄下，需先設定 DATABASE_URL 同本機 Docker DB/Redis 起咗）：

    DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" \
        .venv/bin/python -m scripts.crawler.crawl --limit 20

選項：
    --limit N      最多匯入幾多部（預設 20）
    --dry-run      只打印會匯入嘅內容，唔寫入 DB
    --delay S      每個 HTTP 請求之間嘅間隔秒數（預設 0.6，保持禮貌）
    --source NAME  來源（hongguo / youku / fanqie / douyin / all）
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import httpx

# 令 `python -m scripts...` 可以由 backend/ 目錄直接執行
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.database import SessionLocal  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.drama import Drama  # noqa: E402
from app.models.episode import Episode  # noqa: E402
from scripts.crawler.douyin import DouyinCrawler  # noqa: E402
from scripts.crawler.fanqie import FanqieCrawler  # noqa: E402
from scripts.crawler.hongguo import DEFAULT_HEADERS, HongguoCrawler  # noqa: E402
from scripts.crawler.items import ShortDramaItem  # noqa: E402
from scripts.crawler.youku import YoukuCrawler  # noqa: E402

# 來源代碼 → crawler class。「誠實」placeholder（fanqie/douyin）亦註冊埋。
CRAWLERS: dict[str, type] = {
    "hongguo": HongguoCrawler,
    "youku": YoukuCrawler,
    "fanqie": FanqieCrawler,
    "douyin": DouyinCrawler,
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("crawler")

# 簡轉繁 + 對齊平台已有分類嘅少量別名（其餘標籤保留原樣）
CATEGORY_ALIASES = {
    "武侠": "武俠",
    "仙侠": "仙俠",
    "爱情": "愛情",
    "剧情": "劇情",
    "古风": "古風",
    "萌宝": "萌寶",
    "脑洞": "腦洞",
    "逆袭": "逆襲",
    "成长": "成長",
    "乡村": "鄉村",
    "现代": "現代",
    "悬疑": "懸疑",
}


def normalize_category_name(tag: str) -> str:
    tag = tag.strip()
    return CATEGORY_ALIASES.get(tag, tag)


def _auto_slug(name: str) -> str:
    """自動分類 slug：只可用 [a-z0-9-_]，用 name 嘅 hash 保證穩定且唯一。"""
    import hashlib

    digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:10]
    return f"auto-{digest}"


def _sanitize(value: str | None) -> str | None:
    """移除 DB 唔接受嘅控制字元（NUL 等）。"""
    if value is None:
        return None
    cleaned = "".join(ch for ch in value if ch >= " " or ch in "\n\r\t")
    cleaned = cleaned.strip()
    return cleaned or None


def get_or_create_category(db, name: str) -> Category:
    """按分類名搵現有分類，冇就建立（slug 用 ASCII hash，避免撞名兼符合 schema）。"""
    cat = db.query(Category).filter(Category.name == name).first()
    if cat:
        return cat
    cat = Category(name=name, slug=_auto_slug(name))
    db.add(cat)
    db.flush()
    return cat


def _upsert_episodes(db, drama: Drama, item: ShortDramaItem, stats: dict) -> None:
    """將爬到嘅公開集 upsert 入 episodes（按 drama_id + episode_number）。

    只有抽到真實 video_url 嘅集先會寫入/更新；抽唔到片 URL 嘅集唔郁，
    避免用 placeholder 覆蓋已有資料。
    """
    for ep in item.episodes:
        if not ep.video_url:
            continue
        title = _sanitize(ep.title) or f"第{ep.episode_number}集"
        video_url = _sanitize(ep.video_url)
        if not video_url:
            continue
        row = (
            db.query(Episode)
            .filter(Episode.drama_id == drama.id, Episode.episode_number == ep.episode_number)
            .first()
        )
        if row:
            row.title = title
            row.video_url = video_url
            if ep.duration:
                row.duration = ep.duration
            if ep.player_path:
                row.player_path = ep.player_path
            stats["episodes_updated"] += 1
        else:
            db.add(
                Episode(
                    drama_id=drama.id,
                    episode_number=ep.episode_number,
                    title=title,
                    video_url=video_url,
                    duration=ep.duration,
                    player_path=ep.player_path,
                )
            )
            stats["episodes_created"] += 1


def import_items(db, items: list[ShortDramaItem]) -> dict:
    """將爬回嚟嘅劇集 upsert 入平台資料庫（按標題去重），並順帶 upsert 公開集。"""
    stats = {
        "created": 0,
        "updated": 0,
        "categories_created": 0,
        "episodes_created": 0,
        "episodes_updated": 0,
    }
    for item in items:
        title = _sanitize(item.title) or ""
        if not title:
            continue

        category = None
        primary = item.primary_tag
        if primary:
            category = get_or_create_category(db, _sanitize(normalize_category_name(primary)) or normalize_category_name(primary))
            if category.slug.startswith("auto-") and category not in db.new:
                # 呢個分類係今次流程新建（第一次見到）先算
                if not db.query(Category).filter(Category.id == category.id).scalar():
                    stats["categories_created"] += 1

        existing = db.query(Drama).filter(Drama.title == title).first()
        source_code = _sanitize(item.source) or "hongguo"
        fields = dict(
            description=_sanitize(item.description),
            cover_url=_sanitize(item.cover_url),
            category_id=category.id if category else None,
            episode_count=item.episode_count,
            is_completed=item.is_completed,
            source=source_code,
            # hongguo_series_id 只紅果用（on-demand 重簽 signed URL）；其他來源留 None。
            hongguo_series_id=_sanitize(item.series_id) if source_code == "hongguo" else None,
        )
        if existing:
            for k, v in fields.items():
                if v is not None:
                    setattr(existing, k, v)
            drama = existing
            stats["updated"] += 1
        else:
            drama = Drama(title=title, **fields)
            db.add(drama)
            stats["created"] += 1
        db.flush()  # 攞到 drama.id 先可以綁 episodes

        _upsert_episodes(db, drama, item, stats)
    db.commit()
    return stats


async def run(source: str, limit: int, delay: float, with_episodes: bool) -> list[ShortDramaItem]:
    """跑一個或多個來源。``source`` 可以係單一來源，或 ``all``（跑全部已註冊）。"""
    source_keys = list(CRAWLERS.keys()) if source == "all" else [source]
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30.0, follow_redirects=True) as client:
        all_items: list[ShortDramaItem] = []
        per_source = max(limit // max(len(source_keys), 1), 5)
        for key in source_keys:
            cls = CRAWLERS[key]
            crawler = cls(client, request_delay=delay)
            try:
                items = await crawler.crawl(limit=per_source, with_episodes=with_episodes)
            except Exception as exc:  # noqa: BLE001
                log.warning("來源 %s 抓取失敗：%s", key, exc)
                continue
            log.info("來源 %s：爬到 %d 部", key, len(items))
            all_items.extend(items)
        return all_items


def main() -> None:
    parser = argparse.ArgumentParser(description="短劇元資料爬蟲＋匯入平台")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true", help="只打印，唔寫入 DB")
    parser.add_argument("--delay", type=float, default=0.6)
    parser.add_argument(
        "--source",
        default="hongguo",
        choices=["all", *CRAWLERS.keys()],
        help="來源：hongguo / youku / fanqie / douyin / all",
    )
    parser.add_argument(
        "--with-episodes",
        action="store_true",
        help="入 detail/player 頁抽每集真片 URL 並 upsert 入 episodes",
    )
    args = parser.parse_args()

    items = asyncio.run(run(args.source, args.limit, args.delay, args.with_episodes))
    log.info("爬到 %d 部劇", len(items))

    if args.dry_run:
        for i in items[:10]:
            nreal = sum(1 for e in i.episodes if e.video_url)
            print(
                f"[{i.rank or '-'}] {i.title} | {i.primary_tag or '無分類'} | "
                f"{i.episode_count or '?'}集 | 公開真片 {nreal} 集 | 來源ID {i.series_id}"
            )
        print("...")
        print("（dry-run 模式：未有寫入資料庫）")
        return

    db = SessionLocal()
    try:
        stats = import_items(db, items)
        new_cats = db.query(Category).filter(Category.slug.like("auto-%")).count()
        log.info(
            "匯入完成：新增 %d 部、更新 %d 部；auto- 開頭分類共 %d 個；"
            "集數新增 %d、更新 %d",
            stats["created"], stats["updated"], new_cats,
            stats["episodes_created"], stats["episodes_updated"],
        )
        from sqlalchemy import func as _func
        drama_counts = dict(db.query(Drama.source, _func.count(Drama.id)).group_by(Drama.source).all())
        ep_counts = dict(
            db.query(Drama.source, _func.count(Episode.id))
            .join(Episode, Episode.drama_id == Drama.id)
            .filter(Episode.video_url.isnot(None))
            .group_by(Drama.source).all())
        for src in sorted(drama_counts):
            log.info("  來源 %-8s：劇 %d 部、有片可播嘅集 %d", src, drama_counts[src], ep_counts.get(src, 0))
    finally:
        db.close()


if __name__ == "__main__":
    main()
