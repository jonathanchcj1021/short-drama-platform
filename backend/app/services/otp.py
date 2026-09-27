"""OTP 業務邏輯：產生、冷卻、額度、驗證（以 Redis 儲存）。"""
import random
from datetime import date

from app.config import settings


def _code_key(phone: str) -> str:
    return f"otp:code:{phone}"


def _cooldown_key(phone: str) -> str:
    return f"otp:cooldown:{phone}"


def _daily_key(phone: str) -> str:
    return f"otp:daily:{phone}:{date.today().isoformat()}"


def request_otp(redis_client, phone: str) -> dict:
    """產生並儲存 OTP。

    回傳:
        {"ok": True, "code": "123456"}
        {"ok": False, "reason": "cooldown" | "daily_limit"}
    """
    if redis_client.exists(_cooldown_key(phone)):
        return {"ok": False, "reason": "cooldown"}

    dk = _daily_key(phone)
    count = redis_client.get(dk)
    if count is not None and int(count) >= settings.OTP_DAILY_LIMIT:
        return {"ok": False, "reason": "daily_limit"}

    code = f"{random.randint(0, 10 ** settings.OPT_CODE_LENGTH - 1):0{settings.OPT_CODE_LENGTH}d}"
    redis_client.setex(_code_key(phone), settings.OTP_TTL_SECONDS, code)
    redis_client.setex(_cooldown_key(phone), settings.OTP_COOLDOWN_SECONDS, "1")

    pipe = redis_client.pipeline()
    pipe.incr(dk)
    pipe.expire(dk, 86_400)
    pipe.execute()

    return {"ok": True, "code": code}


def verify_otp(redis_client, phone: str, code: str) -> bool:
    """驗證 OTP，成功後刪除驗證碼。"""
    stored = redis_client.get(_code_key(phone))
    if stored is None or stored != code:
        return False
    redis_client.delete(_code_key(phone))
    return True
