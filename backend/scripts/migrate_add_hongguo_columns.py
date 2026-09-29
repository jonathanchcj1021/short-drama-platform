"""一次性 migration：幫 dramas / episodes 加紅果 mapping 欄位。

- dramas.hongguo_series_id：紅果後台 series_id（str, nullable）
- episodes.player_path：紅果 player 頁路徑（str, nullable）

冇用 Alembic，呢個 script 係 idempotent，重複跑都唔會出事。
用法：
    DATABASE_URL=... .venv/bin/python -m scripts.migrate_add_hongguo_columns
"""
from __future__ import annotations

from sqlalchemy import text

from app.database import engine


def main() -> None:
    stmts = [
        "ALTER TABLE dramas ADD COLUMN IF NOT EXISTS hongguo_series_id VARCHAR(64)",
        "ALTER TABLE episodes ADD COLUMN IF NOT EXISTS player_path VARCHAR(255)",
    ]
    with engine.begin() as conn:
        for s in stmts:
            conn.execute(text(s))
            print("OK:", s)
    print("migration done.")


if __name__ == "__main__":
    main()
