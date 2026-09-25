"""Health check endpoint."""

from fastapi import APIRouter, Request, status

from app.core.rate_limit import limiter
from app.schemas.responses import HealthData, SuccessResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=SuccessResponse[HealthData],
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description=(
        "Returns the current health status of the API service. "
        "Use this endpoint for load balancer and uptime monitoring."
    ),
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
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "An unexpected error occurred.",
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "details": None,
                        },
                    }
                }
            },
        },
    },
    tags=["health"],
)
@limiter.limit("100/minute")
async def health_check(request: Request) -> SuccessResponse[HealthData]:
    """Return service health status."""
    return SuccessResponse[HealthData](
        success=True,
        message="Service is healthy.",
        data=HealthData(status="OK"),
    )
