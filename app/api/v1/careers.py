import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.deps import get_current_admin, get_db
from app.models.job_application import JobApplication, JobApplicationStatus
from app.models.job_posting import JobPosting
from app.schemas.job_application import JobApplicationOut, JobApplicationStatusUpdate
from app.schemas.job_posting import JobPostingCreate, JobPostingOut, JobPostingUpdate
from app.services.email import send_application_notification
from app.services.storage import get_resume_signed_url, upload_resume

public_router = APIRouter(prefix="/careers", tags=["careers"])
admin_postings_router = APIRouter(
    prefix="/admin/careers/postings", tags=["admin:careers"], dependencies=[Depends(get_current_admin)]
)
admin_applications_router = APIRouter(
    prefix="/admin/careers/applications", tags=["admin:careers"], dependencies=[Depends(get_current_admin)]
)


@public_router.get("", response_model=list[JobPostingOut])
async def list_open_job_postings(db: AsyncSession = Depends(get_db)) -> list[JobPosting]:
    result = await db.execute(
        select(JobPosting).where(JobPosting.is_open.is_(True)).order_by(JobPosting.created_at.desc())
    )
    return list(result.scalars().all())


@public_router.get("/{slug}", response_model=JobPostingOut)
async def get_open_job_posting(slug: str, db: AsyncSession = Depends(get_db)) -> JobPosting:
    result = await db.execute(
        select(JobPosting).where(JobPosting.slug == slug, JobPosting.is_open.is_(True))
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return item


@public_router.post("/{job_id}/apply", response_model=JobApplicationOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def apply_to_job(
    request: Request,
    job_id: uuid.UUID,
    applicant_name: str = Form(..., max_length=200),
    email: str = Form(..., max_length=320),
    phone: str | None = Form(default=None, max_length=50),
    cover_letter: str | None = Form(default=None, max_length=5000),
    website: str = Form(default="", max_length=200),
    resume: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> JobApplication:
    # Honeypot: silently accept-and-discard bot submissions without revealing the trap.
    if website:
        return JobApplicationOut(
            id=uuid.uuid4(),
            applicant_name=applicant_name,
            email=email,
            phone=phone,
            cover_letter=cover_letter,
            job_posting_id=job_id,
            status=JobApplicationStatus.new,
            created_at=datetime.now(timezone.utc),
        )

    posting = await db.get(JobPosting, job_id)
    if posting is None or not posting.is_open:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")

    resume_path = await upload_resume(resume)

    application = JobApplication(
        applicant_name=applicant_name,
        email=email,
        phone=phone,
        cover_letter=cover_letter,
        resume_path=resume_path,
        job_posting_id=job_id,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    send_application_notification(application, posting.title)

    return application


@admin_postings_router.get("", response_model=list[JobPostingOut])
async def admin_list_job_postings(db: AsyncSession = Depends(get_db)) -> list[JobPosting]:
    result = await db.execute(select(JobPosting).order_by(JobPosting.created_at.desc()))
    return list(result.scalars().all())


@admin_postings_router.get("/{posting_id}", response_model=JobPostingOut)
async def admin_get_job_posting(posting_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> JobPosting:
    item = await db.get(JobPosting, posting_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return item


@admin_postings_router.post("", response_model=JobPostingOut, status_code=status.HTTP_201_CREATED)
async def admin_create_job_posting(payload: JobPostingCreate, db: AsyncSession = Depends(get_db)) -> JobPosting:
    item = JobPosting(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@admin_postings_router.patch("/{posting_id}", response_model=JobPostingOut)
async def admin_update_job_posting(
    posting_id: uuid.UUID, payload: JobPostingUpdate, db: AsyncSession = Depends(get_db)
) -> JobPosting:
    item = await db.get(JobPosting, posting_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@admin_postings_router.delete("/{posting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_job_posting(posting_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    item = await db.get(JobPosting, posting_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    await db.delete(item)
    await db.commit()


@admin_applications_router.get("", response_model=list[JobApplicationOut])
async def admin_list_job_applications(
    job_posting_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)
) -> list[JobApplication]:
    query = select(JobApplication).order_by(JobApplication.created_at.desc())
    if job_posting_id is not None:
        query = query.where(JobApplication.job_posting_id == job_posting_id)
    result = await db.execute(query)
    return list(result.scalars().all())


@admin_applications_router.get("/{application_id}", response_model=JobApplicationOut)
async def admin_get_job_application(application_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await db.get(JobApplication, application_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    out = JobApplicationOut.model_validate(item)
    out.resume_signed_url = await get_resume_signed_url(item.resume_path)
    return out


@admin_applications_router.patch("/{application_id}", response_model=JobApplicationOut)
async def admin_update_job_application_status(
    application_id: uuid.UUID, payload: JobApplicationStatusUpdate, db: AsyncSession = Depends(get_db)
) -> JobApplication:
    item = await db.get(JobApplication, application_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    item.status = payload.status
    await db.commit()
    await db.refresh(item)
    return item
