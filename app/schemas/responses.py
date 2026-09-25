"""Standard API response envelope schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error detail for API responses."""

    code: str = Field(..., description="Stable machine-readable error code.")
    details: Any = Field(
        default=None,
        description="Optional field-level or contextual error details.",
    )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(default=False, description="Always false for errors.")
    message: str = Field(..., description="UI-safe human-readable error message.")
    error: ErrorDetail = Field(..., description="Structured error metadata.")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""

    success: bool = Field(default=True, description="Always true for success.")
    message: str = Field(..., description="Human-readable success message.")
    data: T = Field(..., description="Response payload.")


class HealthData(BaseModel):
    """Health check response payload."""

    status: str = Field(
        ...,
        description="Service health status.",
        examples=["OK"],
    )


class ValidationErrorItem(BaseModel):
    """Single field validation error."""

    field: str = Field(..., description="Field path that failed validation.")
    message: str = Field(..., description="Validation error message.")


# --- OpenAPI documentation helpers (not used at runtime) ---

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
        "details": [
            {"field": "password", "message": "Field required"},
        ],
    },
}

OPENAPI_ERROR_EXAMPLE_RATE_LIMIT: dict[str, Any] = {
    "success": False,
    "message": "Rate limit exceeded. Please try again later.",
    "error": {"code": "RATE_LIMIT_EXCEEDED", "details": None},
}

OPENAPI_ERROR_EXAMPLE_INTERNAL: dict[str, Any] = {
    "success": False,
    "message": "An unexpected error occurred.",
    "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
}


def openapi_error_response(
    status_code: int,
    description: str,
    example: dict[str, Any] | None = None,
    examples: dict[str, Any] | None = None,
) -> dict[int, dict[str, Any]]:
    """Build a FastAPI responses entry for a documented error status code."""
    content: dict[str, Any] = {
        "application/json": {
            "schema": {"$ref": "#/components/schemas/ErrorResponse"},
        }
    }
    if example is not None:
        content["application/json"]["example"] = example
    if examples is not None:
        content["application/json"]["examples"] = examples
    return {
        status_code: {
            "description": description,
            "content": content,
        }
    }
