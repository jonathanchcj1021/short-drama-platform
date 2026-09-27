"""分類 Schema。"""
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    slug: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-z0-9\-_]+$")
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    slug: str | None = Field(None, min_length=1, max_length=64, pattern=r"^[a-z0-9\-_]+$")
    description: str | None = None


class CategoryOut(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
