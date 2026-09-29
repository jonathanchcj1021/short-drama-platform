"""廣告影片模型。"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    # 時長（秒），預設 20 秒
    duration: Mapped[int] = mapped_column(Integer, nullable=False, server_default="20")
    # 是否啟用（True=啟用，會俾播放端抽到）
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=func.true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
