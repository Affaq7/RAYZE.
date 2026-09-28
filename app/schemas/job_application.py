import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.job_application import JobApplicationStatus


class JobApplicationCreate(BaseModel):
    applicant_name: str = Field(..., max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    cover_letter: str | None = Field(default=None, max_length=5000)
    # Honeypot: real users never fill this in. Bots that autofill every field will.
    website: str = Field(default="", max_length=200)


class JobApplicationStatusUpdate(BaseModel):
    status: JobApplicationStatus


class JobApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    applicant_name: str
    email: str
    phone: str | None
    cover_letter: str | None
    job_posting_id: uuid.UUID
    status: JobApplicationStatus
    created_at: datetime
    # Populated on demand by the admin detail endpoint; short-lived signed URL, never persisted.
    resume_signed_url: str | None = None
