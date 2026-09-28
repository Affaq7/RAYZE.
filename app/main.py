from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.middleware.exception_handling import ExceptionHandlingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()
setup_logging(settings.environment)


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAYZE API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Added first (innermost user middleware) so it catches exceptions
    # right after they leave the router, before ProxyHeaders/SecurityHeaders/
    # CORS ever see them as exceptions -- see ExceptionHandlingMiddleware's
    # docstring for why this can't be a plain app.exception_handler(Exception).
    app.add_middleware(ExceptionHandlingMiddleware)

    # Trust X-Forwarded-Proto/X-Forwarded-For from Render's edge proxy so
    # request.url.scheme and request.client reflect the original client,
    # not the internal proxy hop. Required for HSTS and rate-limit keying.
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

    app.add_middleware(SecurityHeadersMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Invalid request data"},
        )

    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
