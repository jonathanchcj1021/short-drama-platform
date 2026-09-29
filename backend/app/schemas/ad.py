"""廣告影片 Schema。"""
from datetime import datetime

from pydantic import BaseModel, Field


class AdOut(BaseModel):
    id: int
    title: str
    video_url: str
    duration: int
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    duration: int | None = Field(None, ge=1)
    active: bool | None = None
