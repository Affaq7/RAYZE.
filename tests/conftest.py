import os

os.environ.setdefault("SUPABASE_DB_URL", "postgresql+asyncpg://user:pass@localhost:5432/test")
os.environ.setdefault("SUPABASE_URL", "https://test-project.supabase.co")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("RESEND_API_KEY", "test-resend-key")
os.environ.setdefault("RESEND_FROM_EMAIL", "RAYZE <test@example.com>")
os.environ.setdefault("TEAM_NOTIFICATION_EMAIL", "team@example.com")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.deps import get_current_admin, get_db
from app.main import app


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def client_no_db():
    """A TestClient with no DB dependency override -- for routes/tests that
    never touch the database (e.g. auth checks, honeypot short-circuits)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_claims():
    return {"sub": "11111111-1111-1111-1111-111111111111", "email": "admin@example.com", "role": "authenticated"}


@pytest.fixture
def client_as_admin(admin_claims):
    app.dependency_overrides[get_current_admin] = lambda: admin_claims
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_admin, None)
