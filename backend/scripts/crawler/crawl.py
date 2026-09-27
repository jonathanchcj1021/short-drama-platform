"""短劇爬蟲 CLI + 匯入平台資料庫。

用法（喺 backend/ 目錄下，需先設定 DATABASE_URL 同本機 Docker DB/Redis 起咗）：

    DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" \
        .venv/bin/python -m scripts.crawler.crawl --limit 20

選項：
    --limit N      最多匯入幾多部（預設 20）
    --dry-run      只打印會匯入嘅內容，唔寫入 DB
    --delay S      每個 HTTP 請求之間嘅間隔秒數（預設 0.6，保持禮貌）
    --source NAME  來源（目前只有 hongguo）
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
from scripts.crawler.hongguo import DEFAULT_HEADERS, HongguoCrawler  # noqa: E402
from scripts.crawler.items import ShortDramaItem  # noqa: E402

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


def import_items(db, items: list[ShortDramaItem]) -> dict:
    """將爬回嚟嘅劇集 upsert 入平台資料庫（按標題去重）。"""
    stats = {"created": 0, "updated": 0, "categories_created": 0}
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
        fields = dict(
            description=_sanitize(item.description),
            cover_url=_sanitize(item.cover_url),
            category_id=category.id if category else None,
            episode_count=item.episode_count,
            is_completed=item.is_completed,
        )
        if existing:
            for k, v in fields.items():
                if v is not None:
                    setattr(existing, k, v)
            stats["updated"] += 1
        else:
            db.add(Drama(title=title, **fields))
            stats["created"] += 1
    db.commit()
    return stats


async def run(source: str, limit: int, delay: float) -> list[ShortDramaItem]:
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=30.0, follow_redirects=True) as client:
        if source == "hongguo":
            crawler = HongguoCrawler(client, request_delay=delay)
            return await crawler.crawl(limit=limit)
        raise ValueError(f"未知來源: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description="短劇元資料爬蟲＋匯入平台")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true", help="只打印，唔寫入 DB")
    parser.add_argument("--delay", type=float, default=0.6)
    parser.add_argument("--source", default="hongguo", choices=["hongguo"])
    args = parser.parse_args()

    items = asyncio.run(run(args.source, args.limit, args.delay))
    log.info("爬到 %d 部劇", len(items))

    if args.dry_run:
        for i in items[:10]:
            print(
                f"[{i.rank or '-'}] {i.title} | {i.primary_tag or '無分類'} | "
                f"{i.episode_count or '?'}集 | {i.heat or '?'}萬熱度 | 來源ID {i.series_id}"
            )
        print("...")
        print("（dry-run 模式：未有寫入資料庫）")
        return

    db = SessionLocal()
    try:
        stats = import_items(db, items)
        new_cats = db.query(Category).filter(Category.slug.like("auto-%")).count()
        log.info(
            "匯入完成：新增 %d 部、更新 %d 部；auto- 開頭分類共 %d 個",
            stats["created"], stats["updated"], new_cats,
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
