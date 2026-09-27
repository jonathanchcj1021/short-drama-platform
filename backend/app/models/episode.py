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

    drama: Mapped["Drama"] = relationship(back_populates="episodes")  # noqa: F821
