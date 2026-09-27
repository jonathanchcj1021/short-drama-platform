"""pytest fixtures：使用記憶體 SQLite + fakeredis，不需外部 PostgreSQL/Redis。"""
import os

# 必須在匯入 app 之前設定測試環境變數
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

import fakeredis  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.deps import get_redis  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """每個測試前清空所有業務資料。"""
    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture
def fake_redis():
    client = fakeredis.FakeRedis(decode_responses=True)
    yield client
    client.flushall()
    client.close()


@pytest.fixture(autouse=True)
def override_redis(fake_redis):
    app.dependency_overrides[get_redis] = lambda: fake_redis
    yield
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client, fake_redis):
    """完成 OTP 登入並回傳 (headers, token_payload)。

    測試用戶預設提升為管理員（CMS 測試需要）；如需測「普通用戶被拒」，
    請自行建立非 admin 用戶。
    """

    def _make(phone: str = "+886900000001"):
        r = client.post("/auth/otp/request", json={"phone_number": phone})
        assert r.status_code == 200, r.text
        code = fake_redis.get(f"otp:code:{phone}")
        assert code is not None
        r = client.post("/auth/otp/verify", json={"phone_number": phone, "code": code})
        assert r.status_code == 200, r.text
        data = r.json()
        # 提升為 admin，畀 CMS 測試用
        db = SessionLocal()
        try:
            user = db.get(User, data["user"]["id"])
            if user is not None:
                user.is_admin = True
                db.commit()
        finally:
            db.close()
        return {"Authorization": f"Bearer {data['access_token']}"}, data

    return _make
