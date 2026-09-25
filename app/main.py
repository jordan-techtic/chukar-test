"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.core.logging import logger, setup_logging
from app.exceptions.http_exceptions import AppHTTPException
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.schemas.responses import ErrorDetail, ErrorResponse, ValidationErrorItem

def _build_error_response(
    message: str,
    code: str,
    details=None,
) -> dict:
    """Build a standard error response dictionary."""
    return ErrorResponse(
        success=False,
        message=message,
        error=ErrorDetail(code=code, details=details),
    ).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Format Pydantic validation errors into a structured response."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []) if loc != "body")
            errors.append(
                ValidationErrorItem(
                    field=field or "body",
                    message=error.get("msg", "Invalid value."),
                ).model_dump()
            )
        logger.warning("Validation error on {}: {}", request.url.path, errors)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_build_error_response(
                message="Validation error.",
                code="VALIDATION_ERROR",
                details=errors,
            ),
        )

    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        request: Request,
        exc: AppHTTPException,
    ) -> JSONResponse:
        """Handle custom application HTTP exceptions."""
        logger.warning(
            "App error on {}: {} ({})",
            request.url.path,
            exc.message,
            exc.code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_response(
                message=exc.message,
                code=exc.code,
                details=exc.details,
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle FastAPI/Starlette HTTP exceptions."""
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
        }
        message = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_response(
                message=message,
                code=code_map.get(exc.status_code, "HTTP_ERROR"),
                details=exc.detail if not isinstance(exc.detail, str) else None,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions without leaking internals."""
        logger.exception("Unhandled error on {}: {}", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_build_error_response(
                message="An unexpected error occurred.",
                code="INTERNAL_SERVER_ERROR",
                details=None,
            ),
        )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()
    settings = get_settings()

    app = FastAPI(
        title="Marketing Content Calendar API",
        description=(
            "Backend API for the Marketing Content Calendar application. "
            "Provides authentication, marketing activity management, "
            "and Klaviyo performance integration."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        """Root redirect info."""
        return {"message": "Marketing Content Calendar API", "docs": "/docs"}

    logger.info("Application started in {} environment", settings.environment)
    return app


app = create_app()
