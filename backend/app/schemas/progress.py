"""觀看進度 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProgressReport(BaseModel):
    # 前端送 position_sec / duration_sec；向後兼容舊欄位名 current_time / duration。
    model_config = ConfigDict(populate_by_name=True)

    current_time: int = Field(..., ge=0, alias="position_sec")  # 秒
    duration: int | None = Field(None, ge=0, alias="duration_sec")
    completed: bool = False


class ProgressOut(BaseModel):
    episode_id: int
    current_time: int
    duration: int | None = None
    completed: bool
    updated_at: datetime

    model_config = {"from_attributes": True}
