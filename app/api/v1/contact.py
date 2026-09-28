import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.deps import get_current_admin, get_db
from app.models.contact_submission import ContactSubmission, ContactSubmissionStatus
from app.schemas.contact_submission import (
    ContactSubmissionCreate,
    ContactSubmissionOut,
    ContactSubmissionStatusUpdate,
)
from app.services.email import send_contact_notification
from app.services.leads import sync_to_google_sheet

public_router = APIRouter(prefix="/contact", tags=["contact"])
admin_router = APIRouter(
    prefix="/admin/contact-submissions", tags=["admin:contact"], dependencies=[Depends(get_current_admin)]
)


@public_router.post("", response_model=ContactSubmissionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def submit_contact_form(
    request: Request, payload: ContactSubmissionCreate, db: AsyncSession = Depends(get_db)
):
    # Honeypot: silently accept-and-discard bot submissions without revealing the trap.
    if payload.website:
        return ContactSubmissionOut(
            id=uuid.uuid4(),
            name=payload.name,
            email=payload.email,
            company=payload.company,
            message=payload.message,
            is_lead=True,
            status=ContactSubmissionStatus.new,
            created_at=datetime.now(timezone.utc),
        )

    submission = ContactSubmission(
        name=payload.name,
        email=payload.email,
        company=payload.company,
        message=payload.message,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    send_contact_notification(submission)
    sync_to_google_sheet(submission)  # TODO: not wired up yet, see app/services/leads.py

    return submission


@admin_router.get("", response_model=list[ContactSubmissionOut])
async def admin_list_contact_submissions(db: AsyncSession = Depends(get_db)) -> list[ContactSubmission]:
    result = await db.execute(select(ContactSubmission).order_by(ContactSubmission.created_at.desc()))
    return list(result.scalars().all())


@admin_router.get("/{submission_id}", response_model=ContactSubmissionOut)
async def admin_get_contact_submission(
    submission_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ContactSubmission:
    item = await db.get(ContactSubmission, submission_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return item


@admin_router.patch("/{submission_id}", response_model=ContactSubmissionOut)
async def admin_update_contact_submission(
    submission_id: uuid.UUID, payload: ContactSubmissionStatusUpdate, db: AsyncSession = Depends(get_db)
) -> ContactSubmission:
    item = await db.get(ContactSubmission, submission_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
