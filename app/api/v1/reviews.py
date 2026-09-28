import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_admin, get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate

public_router = APIRouter(prefix="/reviews", tags=["reviews"])
admin_router = APIRouter(prefix="/admin/reviews", tags=["admin:reviews"], dependencies=[Depends(get_current_admin)])


@public_router.get("", response_model=list[ReviewOut])
async def list_published_reviews(db: AsyncSession = Depends(get_db)) -> list[Review]:
    result = await db.execute(
        select(Review).where(Review.is_published.is_(True)).order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())


@admin_router.get("", response_model=list[ReviewOut])
async def admin_list_reviews(db: AsyncSession = Depends(get_db)) -> list[Review]:
    result = await db.execute(select(Review).order_by(Review.created_at.desc()))
    return list(result.scalars().all())


@admin_router.get("/{review_id}", response_model=ReviewOut)
async def admin_get_review(review_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Review:
    item = await db.get(Review, review_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return item


@admin_router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def admin_create_review(payload: ReviewCreate, db: AsyncSession = Depends(get_db)) -> Review:
    item = Review(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@admin_router.patch("/{review_id}", response_model=ReviewOut)
async def admin_update_review(
    review_id: uuid.UUID, payload: ReviewUpdate, db: AsyncSession = Depends(get_db)
) -> Review:
    item = await db.get(Review, review_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@admin_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_review(review_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    item = await db.get(Review, review_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    await db.delete(item)
    await db.commit()
