"""Google OAuth 登入：授權導向 + 回調換 token + 建立/更新使用者。

設定（環境變數 / .env）：
    GOOGLE_SSO_ENABLED=true
    GOOGLE_CLIENT_ID=<Google OAuth Client ID>
    GOOGLE_CLIENT_SECRET=<Google OAuth Client Secret>
    GOOGLE_REDIRECT_URI=<本服務>/auth/google/callback
    WEB_APP_URL=<登入完成後跳返嘅網站>
"""
import logging
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_db, get_redis
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import TokenPair, UserOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def _state_key(state: str) -> str:
    return f"oauth:state:{state}"


def _redirect_with_error(message: str) -> RedirectResponse:
    return RedirectResponse(
        f"{settings.WEB_APP_URL}/login/?error={urlencode({'error': message})}",
        status_code=302,
    )


def _require_enabled() -> None:
    if not settings.GOOGLE_SSO_ENABLED:
        raise HTTPException(status_code=404, detail="Google 登入尚未啟用")


@router.get("/authorize")
def google_authorize(redis_client=Depends(get_redis)):
    _require_enabled()

    state = secrets.token_urlsafe(24)
    redis_client.setex(_state_key(state), 600, "1")

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}", status_code=302)


@router.get("/callback")
async def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    _require_enabled()

    # 防 CSRF：state 必須存在且一次性
    if not redis_client.get(_state_key(state)):
        return _redirect_with_error("state 無效或已過期，請重新登入")
    redis_client.delete(_state_key(state))

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_res = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_res.raise_for_status()
            google_access_token = token_res.json()["access_token"]

            userinfo_res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"},
            )
            userinfo_res.raise_for_status()
            info = userinfo_res.json()
    except Exception as exc:  # Google 任一環節失敗
        logger.exception("Google OAuth 交換失敗: %s", exc)
        return _redirect_with_error("Google 登入失敗，請稍後再試")

    email = (info.get("email") or "").strip().lower()
    if not email:
        return _redirect_with_error("Google 帳號缺少 email，無法登入")

    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, nickname=info.get("name"))
        db.add(user)
        db.commit()
        db.refresh(user)

    pair = TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )

    # token 放 URL fragment（#），唔會送去 server，靜態網站讀 location.hash 即可
    redirect_url = (
        f"{settings.WEB_APP_URL}/login/"
        f"#access_token={pair.access_token}&refresh_token={pair.refresh_token}"
    )
    return RedirectResponse(redirect_url, status_code=302)
