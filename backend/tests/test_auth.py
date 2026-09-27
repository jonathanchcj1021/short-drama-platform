"""OTP 登入流程測試。"""


def test_request_otp_stores_code_in_redis(client, fake_redis):
    r = client.post("/auth/otp/request", json={"phone_number": "+886900000001"})
    assert r.status_code == 200
    assert r.json()["message"] == "OTP 已發送"
    code = fake_redis.get("otp:code:+886900000001")
    assert code is not None and len(code) == 6


def test_request_otp_cooldown_blocks_second_request(client, fake_redis):
    r1 = client.post("/auth/otp/request", json={"phone_number": "+886900000002"})
    assert r1.status_code == 200
    r2 = client.post("/auth/otp/request", json={"phone_number": "+886900000002"})
    assert r2.status_code == 429


def test_verify_wrong_code_rejected(client, fake_redis):
    client.post("/auth/otp/request", json={"phone_number": "+886900000003"})
    r = client.post("/auth/otp/verify", json={"phone_number": "+886900000003", "code": "000000"})
    assert r.status_code == 400


def test_verify_correct_code_returns_tokens_and_creates_user(client, fake_redis):
    client.post("/auth/otp/request", json={"phone_number": "+886900000004"})
    code = fake_redis.get("otp:code:+886900000004")
    r = client.post("/auth/otp/verify", json={"phone_number": "+886900000004", "code": code})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["phone_number"] == "+886900000004"

    # /auth/me 帶 access token 可取得使用者
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["phone_number"] == "+886900000004"


def test_me_without_token_unauthorized(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_refresh_returns_new_access_token(client, fake_redis):
    client.post("/auth/otp/request", json={"phone_number": "+886900000005"})
    code = fake_redis.get("otp:code:+886900000005")
    r = client.post("/auth/otp/verify", json={"phone_number": "+886900000005", "code": code})
    refresh_token = r.json()["refresh_token"]

    r2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r2.status_code == 200
    assert r2.json()["access_token"]

    # 用 refresh token 當 access token 應被拒絕
    bad = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert bad.status_code == 401
