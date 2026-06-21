import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import contact, health, metrics
from app.core.config import Settings, get_settings
from app.core.exceptions import INTERNAL_ERROR, VALIDATION_ERROR
from app.core.logger import configure_logging
from app.core.rate_limit import limiter
from app.db.database import create_database_schema

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    configure_logging(settings)
    logger.info("Starting %s env=%s", settings.app_name, settings.app_env)

    if settings.auto_create_tables:
        await create_database_schema()

    yield

    logger.info("Stopping %s", settings.app_name)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Developer portfolio API with contact processing and AI classification.",
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)
    register_exception_handlers(app)

    app.include_router(contact.router, prefix=settings.api_prefix)
    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(metrics.router, prefix=settings.api_prefix)
    app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
    return app


async def request_logging_middleware(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "error": VALIDATION_ERROR.code,
                "message": VALIDATION_ERROR.message,
                "details": exc.errors(),
            },
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        logger.info("Rate limit exceeded on %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"error": "rate_limit_exceeded", "message": str(exc.detail)},
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": INTERNAL_ERROR.code, "message": INTERNAL_ERROR.message},
        )


app = create_app()
