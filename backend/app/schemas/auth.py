"""認證相關 Schema。"""
from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator


class OTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[0-9]{6,20}$")


class OTPVerify(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[0-9]{6,20}$")
    code: str = Field(..., pattern=r"^[0-9]{4,8}$")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    phone_number: str | None = None
    email: str | None = None
    nickname: str | None = None
    is_admin: bool = False
    membership_tier: str = "free"
    vip_expires_at: datetime | None = None
    # 實際係咪有效 VIP（由 membership_tier + vip_expires_at 即時計算，唔靠 ORM 預填）
    is_vip: bool = False

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def _compute_is_vip(self) -> "UserOut":
        if self.membership_tier in ("vip_monthly", "vip_yearly") and self.vip_expires_at is not None:
            exp = self.vip_expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            self.is_vip = exp > datetime.now(timezone.utc)
        else:
            self.is_vip = False
        return self


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """帳號密碼登入：identifier 可以係 email 或手機號碼。"""
    identifier: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class RegisterRequest(BaseModel):
    """公開註冊：email + 密碼 + 暱稱（選填）。"""
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: str | None = Field(None, max_length=64)
