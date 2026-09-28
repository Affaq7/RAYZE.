from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_supabase_jwt
from app.db.session import get_db as _get_db

get_db = _get_db


async def get_current_admin(claims: dict = Depends(verify_supabase_jwt)) -> dict:
    return claims


DbSession = AsyncSession
