import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    client_name: str = Field(..., max_length=200)
    company: str | None = Field(default=None, max_length=200)
    avatar_url: str | None = Field(default=None, max_length=1000)
    quote: str = Field(..., max_length=2000)
    rating: int = Field(..., ge=1, le=5)
    is_published: bool = False


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    client_name: str | None = Field(default=None, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    avatar_url: str | None = Field(default=None, max_length=1000)
    quote: str | None = Field(default=None, max_length=2000)
    rating: int | None = Field(default=None, ge=1, le=5)
    is_published: bool | None = None


class ReviewOut(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
