"""Standard API response envelope schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ValidationErrorItem(BaseModel):
    """Single field-level validation error."""

    field: str = Field(..., description="Request field that failed validation.")
    message: str = Field(..., description="Human-readable validation message.")


class ErrorDetail(BaseModel):
    """Structured error payload returned to clients."""

    code: str = Field(..., description="Stable machine-readable error code.")
    details: list[ValidationErrorItem] | None = Field(
        default=None,
        description="Optional field-level validation details.",
    )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(default=False, description="Always false for errors.")
    message: str = Field(..., description="UI-safe error message.")
    error: ErrorDetail = Field(..., description="Structured error information.")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: bool = Field(default=True, description="Always true for successes.")
    message: str = Field(..., description="Human-readable success message.")
    data: T = Field(..., description="Response payload.")


class HealthData(BaseModel):
    """Health check payload."""

    status: str = Field(..., description="Service health status.", examples=["OK"])


OPENAPI_ERROR_EXAMPLE_INVALID_CREDENTIALS: dict[str, Any] = {
    "success": False,
    "message": "Invalid email/username or password.",
    "error": {"code": "INVALID_CREDENTIALS", "details": None},
}

OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE: dict[str, Any] = {
    "success": False,
    "message": "Your account is inactive. Contact an administrator.",
    "error": {"code": "ACCOUNT_INACTIVE", "details": None},
}

OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED: dict[str, Any] = {
    "success": False,
    "message": "You are not authorized to access this application.",
    "error": {"code": "ACCESS_DENIED", "details": None},
}

OPENAPI_ERROR_EXAMPLE_VALIDATION: dict[str, Any] = {
    "success": False,
    "message": "Validation error.",
    "error": {
        "code": "VALIDATION_ERROR",
        "details": [{"field": "password", "message": "Field required"}],
    },
}

OPENAPI_ERROR_EXAMPLE_RATE_LIMIT: dict[str, Any] = {
    "success": False,
    "message": "Rate limit exceeded. Please try again later.",
    "error": {"code": "RATE_LIMIT_EXCEEDED", "details": None},
}

OPENAPI_ERROR_EXAMPLE_INTERNAL: dict[str, Any] = {
    "success": False,
    "message": "An unexpected error occurred. Please try again later.",
    "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
}


def openapi_error_response(
    status_code: int,
    description: str,
    example: dict[str, Any],
) -> dict[str, Any]:
    """Build an OpenAPI response entry for documented error cases."""
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": example,
                }
            },
        }
    }
