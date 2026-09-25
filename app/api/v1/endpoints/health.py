"""Health check endpoint."""

from fastapi import APIRouter, Request, status

from app.core.config import get_settings
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
        "Use this endpoint for load balancer probes, uptime monitoring, and "
        "deployment readiness checks. Does not require authentication."
    ),
    operation_id="healthCheck",
    responses={
        200: {
            "description": "Service is healthy.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Service is healthy.",
                        "data": {"status": "OK"},
                    }
                }
            },
        },
        **openapi_error_response(
            429,
            "Rate limit exceeded.",
            example=OPENAPI_ERROR_EXAMPLE_RATE_LIMIT,
        ),
        **openapi_error_response(
            500,
            "Internal server error.",
            example=OPENAPI_ERROR_EXAMPLE_INTERNAL,
        ),
    },
    tags=["health"],
    openapi_extra={"security": []},
)
@limiter.limit(lambda: get_settings().rate_limit_health)
async def health_check(request: Request) -> SuccessResponse[HealthData]:
    """Return service health status."""
    return SuccessResponse[HealthData](
        success=True,
        message="Service is healthy.",
        data=HealthData(status="OK"),
    )
