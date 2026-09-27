"""認證相關 Schema。"""
from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[0-9]{6,20}$")


class OTPVerify(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[0-9]{6,20}$")
    code: str = Field(..., pattern=r"^[0-9]{4,8}$")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    phone_number: str
    nickname: str | None = None

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
