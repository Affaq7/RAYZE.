from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard hardening headers to every response.

    HSTS is only added when the request is HTTPS. Render terminates TLS at its
    edge and forwards plain HTTP to the app, so `request.url.scheme` only
    reflects the original client's scheme when the app trusts
    `X-Forwarded-Proto` — see the ProxyHeadersMiddleware wrapping in main.py
    and the `--proxy-headers` uvicorn flag documented in the README.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"

        return response
