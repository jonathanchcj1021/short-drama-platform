"""劇集 Schema。"""
from pydantic import BaseModel, Field

from app.schemas.category import CategoryOut
from app.schemas.episode import EpisodeOut


class DramaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    cover_url: str | None = Field(None, max_length=1024)
    category_id: int | None = None
    release_year: int | None = Field(None, ge=1900, le=2100)
    episode_count: int | None = Field(None, ge=0)
    is_completed: bool = False


class DramaCreate(DramaBase):
    pass


class DramaUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    cover_url: str | None = Field(None, max_length=1024)
    category_id: int | None = None
    release_year: int | None = Field(None, ge=1900, le=2100)
    episode_count: int | None = Field(None, ge=0)
    is_completed: bool | None = None


class DramaOut(DramaBase):
    id: int
    category: CategoryOut | None = None
    # 來源平台代碼（"hongguo" = 紅果短劇），後端回填，CMS 不需填
    source: str = "hongguo"

    model_config = {"from_attributes": True}


class DramaDetail(DramaOut):
    episodes: list[EpisodeOut] = []
