"""Custom HTTP exception classes for application errors."""


class AppHTTPException(Exception):
    """Base application HTTP exception with status code and stable error code."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
    ) -> None:
        """Initialize with a UI-safe message, machine-readable code, and HTTP status."""
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class BadRequestError(AppHTTPException):
    """HTTP 400 bad request."""

    def __init__(self, message: str = "Bad request.", code: str = "BAD_REQUEST") -> None:
        super().__init__(message=message, code=code, status_code=400)


class UnauthorizedError(AppHTTPException):
    """HTTP 401 unauthorized."""

    def __init__(
        self,
        message: str = "Authentication required.",
        code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(message=message, code=code, status_code=401)


class ForbiddenError(AppHTTPException):
    """HTTP 403 forbidden."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(message=message, code=code, status_code=403)


class NotFoundError(AppHTTPException):
    """HTTP 404 not found."""

    def __init__(
        self,
        message: str = "Resource not found.",
        code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(message=message, code=code, status_code=404)


class ConflictError(AppHTTPException):
    """HTTP 409 conflict."""

    def __init__(
        self,
        message: str = "Resource conflict.",
        code: str = "CONFLICT",
    ) -> None:
        super().__init__(message=message, code=code, status_code=409)


class InternalServerError(AppHTTPException):
    """HTTP 500 internal server error."""

    def __init__(
        self,
        message: str = "An unexpected error occurred. Please try again later.",
        code: str = "INTERNAL_SERVER_ERROR",
    ) -> None:
        super().__init__(message=message, code=code, status_code=500)
