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
    # 係咪收費劇。False = 完全免費；True = 頭 10 集免費、之後要睇廣告或 VIP
    is_paid: bool = True


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
    is_paid: bool | None = None


class DramaOut(DramaBase):
    id: int
    category: CategoryOut | None = None
    # 來源平台代碼（"hongguo" = 紅果短劇），後端回填，CMS 不需填
    source: str = "hongguo"

    model_config = {"from_attributes": True}


class DramaDetail(DramaOut):
    episodes: list[EpisodeOut] = []


class DramaListItem(DramaOut):
    """列表項：比 DramaOut 多一個 DB 真實集數。

    `real_episode_count` 係 `episodes` 表嘅實際行數；同 metadata 欄 `episode_count`
    （crawler/CMS 填）係兩回事——例如優酷劇 `episode_count` 有值（24）但未爬片，
    `real_episode_count` 仍然係 0。
    """

    real_episode_count: int = 0


class DramaListEnvelope(BaseModel):
    """劇集分頁 envelope。"""

    items: list[DramaListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
