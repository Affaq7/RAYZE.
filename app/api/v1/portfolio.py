import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_admin, get_db
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioOut, PortfolioUpdate
from app.services.storage import upload_portfolio_image

public_router = APIRouter(prefix="/portfolio", tags=["portfolio"])
admin_router = APIRouter(prefix="/admin/portfolio", tags=["admin:portfolio"], dependencies=[Depends(get_current_admin)])


@public_router.get("", response_model=list[PortfolioOut])
async def list_published_portfolio(db: AsyncSession = Depends(get_db)) -> list[Portfolio]:
    result = await db.execute(
        select(Portfolio).where(Portfolio.is_published.is_(True)).order_by(Portfolio.created_at.desc())
    )
    return list(result.scalars().all())


@public_router.get("/{slug}", response_model=PortfolioOut)
async def get_published_portfolio_item(slug: str, db: AsyncSession = Depends(get_db)) -> Portfolio:
    result = await db.execute(
        select(Portfolio).where(Portfolio.slug == slug, Portfolio.is_published.is_(True))
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    return item


@admin_router.get("", response_model=list[PortfolioOut])
async def admin_list_portfolio(db: AsyncSession = Depends(get_db)) -> list[Portfolio]:
    result = await db.execute(select(Portfolio).order_by(Portfolio.created_at.desc()))
    return list(result.scalars().all())


@admin_router.get("/{item_id}", response_model=PortfolioOut)
async def admin_get_portfolio(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Portfolio:
    item = await db.get(Portfolio, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    return item


@admin_router.post("", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
async def admin_create_portfolio(payload: PortfolioCreate, db: AsyncSession = Depends(get_db)) -> Portfolio:
    item = Portfolio(**payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@admin_router.patch("/{item_id}", response_model=PortfolioOut)
async def admin_update_portfolio(
    item_id: uuid.UUID, payload: PortfolioUpdate, db: AsyncSession = Depends(get_db)
) -> Portfolio:
    item = await db.get(Portfolio, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@admin_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_portfolio(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    item = await db.get(Portfolio, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    await db.delete(item)
    await db.commit()


@admin_router.post("/{item_id}/image", response_model=PortfolioOut)
async def admin_upload_portfolio_cover_image(
    item_id: uuid.UUID, file: UploadFile, db: AsyncSession = Depends(get_db)
) -> Portfolio:
    item = await db.get(Portfolio, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    item.cover_image_url = await upload_portfolio_image(file)
    await db.commit()
    await db.refresh(item)
    return item
