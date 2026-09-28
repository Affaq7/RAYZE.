import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.contact_submission import ContactSubmissionStatus


class ContactSubmissionCreate(BaseModel):
    name: str = Field(..., max_length=200)
    email: EmailStr
    company: str | None = Field(default=None, max_length=200)
    message: str = Field(..., max_length=5000)
    # Honeypot: real users never fill this in. Bots that autofill every field will.
    website: str = Field(default="", max_length=200)


class ContactSubmissionStatusUpdate(BaseModel):
    status: ContactSubmissionStatus | None = None
    is_lead: bool | None = None


class ContactSubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    company: str | None
    message: str
    is_lead: bool
    status: ContactSubmissionStatus
    created_at: datetime
