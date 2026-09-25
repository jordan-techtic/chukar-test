"""Custom HTTP exception classes for application errors."""

from typing import Any


class AppHTTPException(Exception):
    """Base application HTTP exception with structured error metadata."""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: str,
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class BadRequestError(AppHTTPException):
    """400 Bad Request."""

    def __init__(
        self,
        message: str = "Bad request.",
        code: str = "BAD_REQUEST",
        details: Any = None,
    ) -> None:
        super().__init__(400, message, code, details)


class UnauthorizedError(AppHTTPException):
    """401 Unauthorized."""

    def __init__(
        self,
        message: str = "Authentication required.",
        code: str = "UNAUTHORIZED",
        details: Any = None,
    ) -> None:
        super().__init__(401, message, code, details)


class ForbiddenError(AppHTTPException):
    """403 Forbidden."""

    def __init__(
        self,
        message: str = "Access denied.",
        code: str = "FORBIDDEN",
        details: Any = None,
    ) -> None:
        super().__init__(403, message, code, details)


class NotFoundError(AppHTTPException):
    """404 Not Found."""

    def __init__(
        self,
        message: str = "Resource not found.",
        code: str = "NOT_FOUND",
        details: Any = None,
    ) -> None:
        super().__init__(404, message, code, details)


class ConflictError(AppHTTPException):
    """409 Conflict."""

    def __init__(
        self,
        message: str = "Resource conflict.",
        code: str = "CONFLICT",
        details: Any = None,
    ) -> None:
        super().__init__(409, message, code, details)


class InternalServerError(AppHTTPException):
    """500 Internal Server Error."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        code: str = "INTERNAL_SERVER_ERROR",
        details: Any = None,
    ) -> None:
        super().__init__(500, message, code, details)
