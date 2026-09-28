import uuid

import httpx
from fastapi import HTTPException, UploadFile, status

from app.core.config import Settings, get_settings

_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
_ALLOWED_RESUME_TYPES = {"application/pdf", "image/jpeg", "image/png"}


def _extension_for(content_type: str) -> str:
    return {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "application/pdf": "pdf",
    }.get(content_type, "bin")


async def _read_and_validate(file: UploadFile, allowed_types: set[str], max_size_mb: int) -> bytes:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}",
        )

    max_bytes = max_size_mb * 1024 * 1024
    contents = await file.read()
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {max_size_mb}MB limit",
        )
    return contents


async def _upload_to_bucket(
    settings: Settings, bucket: str, path: str, contents: bytes, content_type: str
) -> None:
    url = f"{settings.supabase_url}/storage/v1/object/{bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": content_type,
        "x-upsert": "false",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, content=contents)
    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload file to storage",
        )


async def upload_portfolio_image(file: UploadFile, settings: Settings | None = None) -> str:
    """Uploads to the public portfolio-images bucket and returns its public URL."""
    settings = settings or get_settings()
    contents = await _read_and_validate(file, _ALLOWED_IMAGE_TYPES, settings.max_image_size_mb)
    path = f"{uuid.uuid4()}.{_extension_for(file.content_type)}"
    await _upload_to_bucket(settings, settings.portfolio_bucket, path, contents, file.content_type)
    return f"{settings.supabase_url}/storage/v1/object/public/{settings.portfolio_bucket}/{path}"


async def upload_resume(file: UploadFile, settings: Settings | None = None) -> str:
    """Uploads to the private resumes bucket and returns only the object path
    (never a public URL) — access is via short-lived signed URLs on demand.
    """
    settings = settings or get_settings()
    contents = await _read_and_validate(file, _ALLOWED_RESUME_TYPES, settings.max_resume_size_mb)
    path = f"{uuid.uuid4()}.{_extension_for(file.content_type)}"
    await _upload_to_bucket(settings, settings.resume_bucket, path, contents, file.content_type)
    return path


async def get_resume_signed_url(
    resume_path: str, settings: Settings | None = None, expires_in_seconds: int = 300
) -> str | None:
    """Requests a short-lived signed URL for a resume from Supabase Storage.
    Generated fresh per request, never persisted.
    """
    if not resume_path:
        return None

    settings = settings or get_settings()
    url = f"{settings.supabase_url}/storage/v1/object/sign/{settings.resume_bucket}/{resume_path}"
    headers = {"Authorization": f"Bearer {settings.supabase_service_role_key}"}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, headers=headers, json={"expiresIn": expires_in_seconds})

    if response.status_code >= 400:
        return None

    signed_path = response.json().get("signedURL")
    if not signed_path:
        return None
    return f"{settings.supabase_url}/storage/v1{signed_path}"
