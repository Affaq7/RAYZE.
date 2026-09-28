import os

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.deps import get_db
from app.main import app
from app.models.portfolio import Portfolio

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL (a real Postgres instance) to run DB-backed integration tests",
)


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with session_factory() as session:
        yield session

    app.dependency_overrides.pop(get_db, None)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_public_portfolio_only_returns_published_items(db_session, client_no_db):
    db_session.add_all(
        [
            Portfolio(
                title="Published Item",
                slug="published-item",
                client_name="Client A",
                category="Video",
                description="desc",
                is_published=True,
            ),
            Portfolio(
                title="Draft Item",
                slug="draft-item",
                client_name="Client B",
                category="Video",
                description="desc",
                is_published=False,
            ),
        ]
    )
    await db_session.commit()

    response = client_no_db.get("/api/v1/portfolio")

    assert response.status_code == 200
    slugs = {item["slug"] for item in response.json()}
    assert slugs == {"published-item"}
