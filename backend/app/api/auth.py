"""認證路由：電話 OTP 登入。"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_redis
from app.core.security import TokenError, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.auth import (
    AccessTokenOut,
    OTPRequest,
    OTPVerify,
    RefreshTokenRequest,
    TokenPair,
    UserOut,
)
from app.services import otp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", status_code=status.HTTP_200_OK)
def request_otp(body: OTPRequest, redis_client=Depends(get_redis)):
    result = otp.request_otp(redis_client, body.phone_number)
    if not result["ok"]:
        if result["reason"] == "cooldown":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="請勿重複發送，請稍後再試",
            )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="今日驗證碼發送次數已達上限",
        )

    # 開發期 mock：直接把驗證碼印在 server log
    logger.info("OTP for %s: %s", body.phone_number, result["code"])
    return {"message": "OTP 已發送"}


@router.post("/otp/verify", response_model=TokenPair)
def verify_otp(body: OTPVerify, db: Session = Depends(get_db), redis_client=Depends(get_redis)):
    if not otp.verify_otp(redis_client, body.phone_number, body.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="驗證碼錯誤或已過期",
        )

    user = db.scalar(select(User).where(User.phone_number == body.phone_number))
    if user is None:
        user = User(phone_number=body.phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=AccessTokenOut)
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在")

    return AccessTokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
