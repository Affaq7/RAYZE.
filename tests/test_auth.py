from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings


def _make_token(secret: str, *, expired: bool = False, audience: str = "authenticated") -> str:
    now = datetime.now(timezone.utc)
    exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    return jwt.encode(
        {"sub": "user-id", "aud": audience, "exp": exp, "role": "authenticated"},
        secret,
        algorithm="HS256",
    )


def test_admin_route_requires_auth_header(client_no_db):
    response = client_no_db.get("/api/v1/admin/portfolio")
    assert response.status_code == 403 or response.status_code == 401


def test_admin_route_rejects_invalid_token(client_no_db):
    response = client_no_db.get(
        "/api/v1/admin/portfolio", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_admin_route_rejects_expired_token(client_no_db):
    settings = get_settings()
    token = _make_token(settings.supabase_jwt_secret, expired=True)
    response = client_no_db.get(
        "/api/v1/admin/portfolio", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_admin_route_rejects_wrong_secret(client_no_db):
    token = _make_token("a-different-secret")
    response = client_no_db.get(
        "/api/v1/admin/portfolio", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
