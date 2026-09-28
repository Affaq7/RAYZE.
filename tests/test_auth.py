from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec


def _make_token(private_key, *, expired: bool = False, audience: str = "authenticated") -> str:
    now = datetime.now(timezone.utc)
    exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
    return jwt.encode(
        {"sub": "user-id", "aud": audience, "exp": exp, "role": "authenticated"},
        private_key,
        algorithm="ES256",
    )


def _mock_jwks(public_key):
    """Patches out the network JWKS lookup so tests can verify real
    jwt.decode() behavior against a locally generated keypair, without
    hitting Supabase's actual JWKS endpoint."""
    fake_client = SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=public_key))
    return patch("app.core.security._jwks_client", return_value=fake_client)


@pytest.fixture(scope="module")
def keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key, private_key.public_key()


def test_admin_route_requires_auth_header(client_no_db):
    response = client_no_db.get("/api/v1/admin/portfolio")
    assert response.status_code in (401, 403)


def test_admin_route_rejects_garbage_token(client_no_db):
    response = client_no_db.get(
        "/api/v1/admin/portfolio", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_admin_route_accepts_valid_token(client_no_db, keypair):
    private_key, public_key = keypair
    token = _make_token(private_key)
    with _mock_jwks(public_key):
        response = client_no_db.get(
            "/api/v1/admin/portfolio", headers={"Authorization": f"Bearer {token}"}
        )
    # Auth passes; the request then fails on the (unreachable, fake) DB --
    # what matters here is that it's not a 401.
    assert response.status_code != 401


def test_admin_route_rejects_expired_token(client_no_db, keypair):
    private_key, public_key = keypair
    token = _make_token(private_key, expired=True)
    with _mock_jwks(public_key):
        response = client_no_db.get(
            "/api/v1/admin/portfolio", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 401


def test_admin_route_rejects_token_signed_by_a_different_key(client_no_db, keypair):
    _, public_key = keypair
    other_private_key = ec.generate_private_key(ec.SECP256R1())
    token = _make_token(other_private_key)
    with _mock_jwks(public_key):
        response = client_no_db.get(
            "/api/v1/admin/portfolio", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 401
