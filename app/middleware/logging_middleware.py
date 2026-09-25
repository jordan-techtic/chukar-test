"""HTTP request/response logging middleware."""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and outgoing responses for all HTTP methods."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log method, path, status, and duration."""
        start = time.perf_counter()
        logger.info("Request: {} {}", request.method, request.url.path)
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Response: {} {} - {} ({:.2f}ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
