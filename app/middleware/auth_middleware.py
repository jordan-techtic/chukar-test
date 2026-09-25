"""JWT authentication middleware and helper utilities."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.logging import logger
from app.core.security import TOKEN_TYPE_ACCESS, verify_jwt_token
from app.schemas.responses import ErrorDetail, ErrorResponse

PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/api/v1/health",
        "/api/v1/marketing-team-member/login",
        "/api/v1/marketing-team-member/forgot-password",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
)


class AuthMiddleware(BaseHTTPMiddleware):
    """Enforce JWT authentication on all non-public routes."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate Bearer token or allow public paths through."""
        path = request.url.path
        if path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    success=False,
                    message="Authentication required.",
                    error=ErrorDetail(code="UNAUTHORIZED", details=None),
                ).model_dump(),
            )

        token = authorization.removeprefix("Bearer ").strip()
        settings = get_settings()
        try:
            payload = verify_jwt_token(token, settings, expected_type=TOKEN_TYPE_ACCESS)
            request.state.user_id = payload.get("sub")
        except Exception as exc:
            logger.warning("Auth middleware rejected token on {}: {}", path, exc)
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    success=False,
                    message="Invalid or expired authentication token.",
                    error=ErrorDetail(code="UNAUTHORIZED", details=None),
                ).model_dump(),
            )

        return await call_next(request)
