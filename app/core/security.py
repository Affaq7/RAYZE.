from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

_bearer_scheme = HTTPBearer(auto_error=True)


@lru_cache
def _jwks_client(supabase_url: str) -> jwt.PyJWKClient:
    # PyJWKClient caches fetched keys internally (keyed by `kid`), so this
    # only hits the network again after a key rotation introduces a new kid.
    return jwt.PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json")


def verify_supabase_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Verify a Supabase-issued JWT against the project's published JWKS
    (not a fixed shared secret) -- Supabase now signs new tokens with
    per-project asymmetric keys (ES256) that rotate over time, and a fixed
    HS256 secret only verifies tokens issued before the most recent
    rotation. Any validly signed, non-expired token is treated as admin --
    there is no roles table; admin identity is fully controlled by who
    exists in the Supabase Auth dashboard.
    """
    token = credentials.credentials
    try:
        signing_key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims
