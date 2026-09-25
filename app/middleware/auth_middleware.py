"""JWT authentication middleware and helper utilities."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging import logger
from app.core.security import verify_jwt_token

PUBLIC_PATHS = {
    "/api/v1/health",
    "/api/v1/marketing-team-member/login",
    "/api/v1/marketing-team-member/forgot-password",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Attach authenticated user context when a valid Bearer token is present.

    Public paths are skipped. Invalid tokens on protected paths are logged but
    not rejected here — route-level Depends(get_current_user) enforces auth.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Optionally decode JWT and attach user id to request state."""
        request.state.user_id = None

        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            try:
                settings = get_settings()
                payload = verify_jwt_token(token, settings)
                request.state.user_id = payload.get("sub")
            except Exception as exc:
                logger.debug("JWT verification failed in middleware: {}", exc)

        return await call_next(request)
