import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Catches any otherwise-unhandled exception and returns a generic 500
    body, with the full traceback going only to server logs.

    This is deliberately a middleware rather than an
    `app.exception_handler(Exception)` registration: Starlette special-cases
    a handler registered for `Exception`/500 onto `ServerErrorMiddleware`,
    which wraps *outside* every user middleware (including CORS and
    security headers). That means such a response would ship with no CORS
    or security headers at all -- to the browser it looks like a CORS
    failure, not a 500, and every hardening header is silently missing on
    exactly the responses where clients most need a defined body.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled exception while processing %s %s", request.method, request.url.path
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
