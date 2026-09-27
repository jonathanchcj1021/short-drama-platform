"""設定／重設使用者密碼。

用法：
    cd backend
    DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/drama" \
        .venv/bin/python -m scripts.set_password <email 或手機號碼> <新密碼>

密碼至少 6 位。
"""
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User


def main() -> None:
    if len(sys.argv) != 3:
        print("用法: python -m scripts.set_password <email 或手機號碼> <新密碼>")
        sys.exit(1)

    identifier = sys.argv[1].strip()
    password = sys.argv[2]
    if len(password) < 6:
        print("密碼至少 6 位")
        sys.exit(1)

    db = SessionLocal()
    try:
        ident_lower = identifier.lower()
        user = db.scalar(
            select(User).where(
                (User.email == ident_lower) | (User.phone_number == identifier)
            )
        )
        if user is None:
            print(f"搵唔到使用者: {identifier}")
            sys.exit(1)

        user.password_hash = hash_password(password)
        db.commit()
        print(f"✅ 已為用戶 id={user.id} ({user.phone_number or user.email}) 設定密碼")
    finally:
        db.close()


if __name__ == "__main__":
    main()
