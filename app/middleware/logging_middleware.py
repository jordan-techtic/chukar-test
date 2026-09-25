"""HTTP request/response logging middleware."""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and outgoing responses with elapsed time."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process a request and log method, path, status, and duration."""
        start = time.perf_counter()
        logger.info("Request: {} {}", request.method, request.url.path)
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Response: {} {} - {} ({:.2f}ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response
