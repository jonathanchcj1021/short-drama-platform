"""會員 / 訂閱共用邏輯。"""
from datetime import datetime, timezone

from app.models.user import User

# 月費 / 年費價錢（HKD）
MONTHLY_PRICE_HKD = 28
YEARLY_PRICE_HKD = 288

# 頭 N 集免費任睇（收費劇先適用）
FREE_EPISODE_LIMIT = 10


def effective_is_vip(user: User) -> bool:
    """統一判定用戶而家係咪有效 VIP。

    條件：membership_tier 係 vip_monthly / vip_yearly，
    且 vip_expires_at 存在，且未過期。過期即作免費。
    """
    if user.membership_tier not in ("vip_monthly", "vip_yearly"):
        return False
    exp = user.vip_expires_at
    if exp is None:
        return False
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp > datetime.now(timezone.utc)
