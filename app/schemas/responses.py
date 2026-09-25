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
