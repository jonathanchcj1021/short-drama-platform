"""訂閱 / 會員狀態路由（模擬付款，唔接 Stripe）。"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.billing import (
    MONTHLY_PRICE_HKD,
    YEARLY_PRICE_HKD,
    effective_is_vip,
)
from app.core.deps import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/billing", tags=["billing"])


def _billing_payload(user: User) -> dict:
    return {
        "membership_tier": user.membership_tier,
        "vip_expires_at": user.vip_expires_at,
        "is_vip": effective_is_vip(user),
        "monthly_price_hkd": MONTHLY_PRICE_HKD,
        "yearly_price_hkd": YEARLY_PRICE_HKD,
    }


@router.get("/me")
def billing_me(current_user: User = Depends(get_current_user)):
    """查自己嘅會員狀態同價錢。"""
    return _billing_payload(current_user)


@router.post("/subscribe")
def subscribe(
    plan: str = Query(..., description="monthly 或 yearly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """模擬付款：直接 set VIP 到期日。

    續訂由現有到期日延長（如果仲有有效 VIP），否則由而家開始計。
    """
    if plan not in ("monthly", "yearly"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="plan 必須係 monthly 或 yearly",
        )

    now = datetime.now(timezone.utc)
    if effective_is_vip(current_user) and current_user.vip_expires_at is not None:
        base = max(now, current_user.vip_expires_at)
    else:
        base = now

    if plan == "monthly":
        current_user.membership_tier = "vip_monthly"
        current_user.vip_expires_at = base + timedelta(days=30)
    else:
        current_user.membership_tier = "vip_yearly"
        current_user.vip_expires_at = base + timedelta(days=365)

    db.commit()
    db.refresh(current_user)
    return _billing_payload(current_user)
