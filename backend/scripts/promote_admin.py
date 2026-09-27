"""將指定用戶提升為管理員（CMS 用）。

用法：
    DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" \
        .venv/bin/python -m scripts.promote_admin 85263106930
    # 亦可以用 email
    DATABASE_URL="..." .venv/bin/python -m scripts.promote_admin someone@example.com
"""
from __future__ import annotations

import sys

from sqlalchemy import or_

from app.database import SessionLocal
from app.models.user import User


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python -m scripts.promote_admin <電話或email>")
        return 1

    ident = sys.argv[1].strip()
    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(or_(User.phone_number == ident, User.email == ident))
            .first()
        )
        if user is None:
            print(f"搵唔到用戶: {ident}")
            return 1
        user.is_admin = True
        db.commit()
        print(
            f"已提升為管理員: id={user.id} "
            f"phone={user.phone_number or '-'} email={user.email or '-'}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
