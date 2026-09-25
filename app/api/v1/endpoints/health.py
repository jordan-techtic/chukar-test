"""Health check endpoint."""

from fastapi import APIRouter, Request, status

from app.core.rate_limit import limiter
from app.schemas.responses import (
    OPENAPI_ERROR_EXAMPLE_INTERNAL,
    OPENAPI_ERROR_EXAMPLE_RATE_LIMIT,
    HealthData,
    SuccessResponse,
    openapi_error_response,
)

router = APIRouter()


@router.get(
    "/health",
    response_model=SuccessResponse[HealthData],
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description=(
        "Returns the current health status of the API service. "
        "Use this endpoint for load balancer probes, uptime monitoring, "
        "and deployment verification. No authentication is required."
    ),
    tags=["health"],
    responses={
        **openapi_error_response(
            429,
            "Rate limit exceeded.",
            OPENAPI_ERROR_EXAMPLE_RATE_LIMIT,
        ),
        **openapi_error_response(
            500,
            "Internal server error.",
            OPENAPI_ERROR_EXAMPLE_INTERNAL,
        ),
    },
)
@limiter.limit("60/minute")
async def health_check(request: Request) -> SuccessResponse[HealthData]:
    """Return service health status."""
    _ = request
    return SuccessResponse(
        success=True,
        message="Service is healthy.",
        data=HealthData(status="OK"),
    )
