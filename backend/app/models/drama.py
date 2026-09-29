"""劇集模型。"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Drama(Base):
    __tablename__ = "dramas"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    episode_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 來源平台代碼（例如 "hongguo" = 紅果短劇），預設 hongguo
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="hongguo", default="hongguo"
    )
    # 紅果後台 series_id（用嚟 on-demand 重新簽 signed video URL），無對應就係 None
    hongguo_series_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    episodes: Mapped[list["Episode"]] = relationship(  # noqa: F821
        back_populates="drama",
        cascade="all, delete-orphan",
        order_by="Episode.episode_number",
    )
    category: Mapped["Category | None"] = relationship("Category", lazy="joined")  # noqa: F821
