import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioBase(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=220, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    client_name: str = Field(..., max_length=200)
    category: str = Field(..., max_length=100)
    description: str = Field(..., max_length=5000)
    cover_image_url: str | None = Field(default=None, max_length=1000)
    gallery: list[str] = Field(default_factory=list, max_length=50)
    is_published: bool = False


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, max_length=220, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    client_name: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    cover_image_url: str | None = Field(default=None, max_length=1000)
    gallery: list[str] | None = Field(default=None, max_length=50)
    is_published: bool | None = None


class PortfolioOut(PortfolioBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
