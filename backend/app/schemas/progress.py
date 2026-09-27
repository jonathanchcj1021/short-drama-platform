"""觀看進度 Schema。"""
from datetime import datetime

from pydantic import BaseModel, Field


class ProgressReport(BaseModel):
    current_time: int = Field(..., ge=0)  # 秒
    duration: int | None = Field(None, ge=0)
    completed: bool = False


class ProgressOut(BaseModel):
    episode_id: int
    current_time: int
    duration: int | None = None
    completed: bool
    updated_at: datetime

    model_config = {"from_attributes": True}
