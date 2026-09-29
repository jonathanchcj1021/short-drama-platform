"""集數 Schema。"""
from pydantic import BaseModel, Field


class EpisodeBase(BaseModel):
    episode_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    video_url: str = Field(..., min_length=1, max_length=1024)
    duration: int | None = Field(None, ge=0)  # 秒
    description: str | None = None


class EpisodeCreate(EpisodeBase):
    drama_id: int


class EpisodeUpdate(BaseModel):
    episode_number: int | None = Field(None, ge=1)
    title: str | None = Field(None, min_length=1, max_length=255)
    video_url: str | None = Field(None, min_length=1, max_length=1024)
    duration: int | None = Field(None, ge=0)
    description: str | None = None


class EpisodeOut(EpisodeBase):
    id: int
    drama_id: int
    # None = 舊直片 mp4（走 media proxy）；'youtube' = YouTube 官方 iframe
    video_type: str | None = None

    model_config = {"from_attributes": True}
