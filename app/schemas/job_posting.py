import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobPostingBase(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=220, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    department: str = Field(..., max_length=100)
    location: str = Field(..., max_length=200)
    employment_type: str = Field(..., max_length=50)
    description: str = Field(..., max_length=5000)
    is_open: bool = True


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    slug: str | None = Field(default=None, max_length=220, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    department: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    employment_type: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=5000)
    is_open: bool | None = None


class JobPostingOut(JobPostingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
