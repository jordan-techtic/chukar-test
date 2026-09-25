"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import logger, setup_logging
from app.core.rate_limit import configure_rate_limiting, limiter
from app.exceptions.http_exceptions import AppHTTPException
from app.middleware.auth_middleware import AuthMiddleware, PUBLIC_PATHS
from app.middleware.logging_middleware import LoggingMiddleware
from app.schemas.responses import ErrorDetail, ErrorResponse, ValidationErrorItem

settings = get_settings()

BEARER_AUTH_SCHEME = "BearerAuth"


def _configure_openapi(app: FastAPI) -> None:
    """Attach a custom OpenAPI schema with JWT Bearer security documentation."""

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            BEARER_AUTH_SCHEME
        ] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT access token obtained from "
                "POST /api/v1/marketing-team-member/login (`data.tokens.access_token`)."
            ),
        }

        for path, path_item in schema.get("paths", {}).items():
            if path in PUBLIC_PATHS:
                for operation in path_item.values():
                    if isinstance(operation, dict):
                        operation["security"] = []

        schema["security"] = [{BEARER_AUTH_SCHEME: []}]
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    setup_logging(settings.environment)

    app = FastAPI(
        title="Marketing Content Calendar API",
        description=(
            "Backend API for the Marketing Content Calendar application. "
            "Public auth endpoints (login, forgot-password, health) require no token. "
            "All other routes require a Bearer JWT access token."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    configure_rate_limiting(app)
    _configure_openapi(app)

    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        request: Request,
        exc: AppHTTPException,
    ) -> JSONResponse:
        """Handle typed application HTTP exceptions."""
        logger.warning(
            "App error on {}: {} ({})",
            request.url.path,
            exc.message,
            exc.code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                success=False,
                message=exc.message,
                error=ErrorDetail(code=exc.code, details=None),
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Format Pydantic/FastAPI validation errors with field-level details."""
        errors: list[ValidationErrorItem] = []
        for error in exc.errors():
            field = ".".join(str(part) for part in error.get("loc", []) if part != "body")
            if not field:
                field = "body"
            errors.append(
                ValidationErrorItem(
                    field=field,
                    message=error.get("msg", "Validation error"),
                )
            )
        logger.warning(
            "Validation error on {}: {}",
            request.url.path,
            [item.model_dump() for item in errors],
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation error.",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "details": [item.model_dump() for item in errors],
                },
            },
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(
        request: Request,
        exc: RateLimitExceeded,
    ) -> JSONResponse:
        """Handle slowapi rate limit violations."""
        _ = exc
        logger.warning("Rate limit exceeded on {}", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=ErrorResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                error=ErrorDetail(code="RATE_LIMIT_EXCEEDED", details=None),
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Normalize Starlette HTTPException into the standard error envelope."""
        logger.warning(
            "HTTP exception on {}: {}",
            request.url.path,
            exc.detail,
        )
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                success=False,
                message=detail,
                error=ErrorDetail(code="HTTP_ERROR", details=None),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch unhandled exceptions and return a generic 500 response."""
        logger.exception("Unhandled error on {}: {}", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                message="An unexpected error occurred. Please try again later.",
                error=ErrorDetail(code="INTERNAL_SERVER_ERROR", details=None),
            ).model_dump(),
        )

    app.include_router(api_router, prefix="/api/v1")
    logger.info("Application started in {} environment", settings.environment)
    return app


app = create_app()
