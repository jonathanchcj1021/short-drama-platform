"""單集模型。"""
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    drama_id: Mapped[int] = mapped_column(
        ForeignKey("dramas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 秒
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 紅果 player 頁路徑（/player/<series_id> 或 /player/<series_id>/<item_id>），
    # 用嚟 on-demand 重新簽 signed video URL；只有公開解鎖嘅集先有。
    player_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # 片種：None = 舊行為直片 mp4（走 media proxy）；'youtube' = YouTube 官方片，
    # 前端要直接 iframe embed（唔經 media proxy）。
    video_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    drama: Mapped["Drama"] = relationship(back_populates="episodes")  # noqa: F821
