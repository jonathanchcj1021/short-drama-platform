"""使用者模型。"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 電話（OTP 登入）同 email（Google 登入）二選一皆可
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # 密碼雜湊（帳號密碼登入）；NULL 表示未設定密碼
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # CMS 管理權限
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    # 會員等級：free / vip_monthly / vip_yearly
    membership_tier: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="free", default="free"
    )
    # VIP 到期日（UTC；NULL 或已過期即視為免費用戶）
    vip_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
