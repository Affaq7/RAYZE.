import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContactSubmissionStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    archived = "archived"


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_lead: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    status: Mapped[ContactSubmissionStatus] = mapped_column(
        Enum(ContactSubmissionStatus, name="contact_submission_status"),
        nullable=False,
        server_default=ContactSubmissionStatus.new.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
