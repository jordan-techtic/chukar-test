"""Annual marketing calendar endpoint."""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.activity import CalendarData
from app.schemas.openapi_marketing_calendar import OPENAPI_SUCCESS_EXAMPLE_CALENDAR
from app.schemas.responses import (
    OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED,
    OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE,
    OPENAPI_ERROR_EXAMPLE_INTERNAL,
    OPENAPI_ERROR_EXAMPLE_RATE_LIMIT,
    OPENAPI_ERROR_EXAMPLE_UNAUTHORIZED,
    OPENAPI_ERROR_EXAMPLE_VALIDATION,
    SuccessResponse,
    openapi_error_response,
    openapi_error_response_examples,
    openapi_success_response,
)
from app.services.calendar_service import CalendarService

router = APIRouter()

_CALENDAR_FORBIDDEN_EXAMPLES = {
    "accountInactive": {
        "summary": "Account inactive",
        "value": OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE,
    },
    "accessDenied": {
        "summary": "Wrong role",
        "value": OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED,
    },
}

_CALENDAR_RESPONSES = {
    **openapi_success_response(
        200,
        "Annual marketing calendar retrieved successfully.",
        OPENAPI_SUCCESS_EXAMPLE_CALENDAR,
    ),
    **openapi_error_response(
        401,
        "Missing or invalid Bearer token.",
        OPENAPI_ERROR_EXAMPLE_UNAUTHORIZED,
    ),
    **openapi_error_response_examples(
        403,
        "Account inactive or role not authorized.",
        _CALENDAR_FORBIDDEN_EXAMPLES,
    ),
    **openapi_error_response(
        422,
        "Invalid query parameters.",
        OPENAPI_ERROR_EXAMPLE_VALIDATION,
    ),
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
}


@router.get(
    "/calendar",
    response_model=SuccessResponse[CalendarData],
    status_code=status.HTTP_200_OK,
    summary="Get annual marketing calendar",
    operation_id="getMarketingCalendar",
    description=(
        "Retrieve the annual marketing calendar with all scheduled activities grouped by date. "
        "Supports year and month navigation via query parameters for seamless browsing.\n\n"
        "Each activity includes a color for calendar display and activity type metadata is "
        "returned for dynamic form rendering on the frontend.\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Navigation:** Use `year` (defaults to current year) and optional `month` (1-12) "
        "to navigate between months and years.\n\n"
        "**Empty state:** Returns `days: []` when no activities are scheduled.\n\n"
        "**Stable error codes:**\n"
        "- `UNAUTHORIZED` (401) — missing or invalid token\n"
        "- `ACCOUNT_INACTIVE` (403) — user deactivated\n"
        "- `ACCESS_DENIED` (403) — wrong role\n"
        "- `INVALID_CALENDAR_MONTH` (400) — month out of range\n"
        "- `VALIDATION_ERROR` (422) — invalid query params\n"
        "- `RATE_LIMIT_EXCEEDED` (429) — too many requests\n"
        "- `INTERNAL_SERVER_ERROR` (500) — unexpected failure"
    ),
    tags=["marketing-team-member"],
    responses=_CALENDAR_RESPONSES,
)
@limiter.limit("60/minute")
async def get_calendar(
    request: Request,
    year: int | None = Query(
        default=None,
        ge=2000,
        le=2100,
        description="Calendar year to display (defaults to current year).",
        examples=[2026],
    ),
    month: int | None = Query(
        default=None,
        ge=1,
        le=12,
        description="Optional month filter (1-12) for month navigation.",
        examples=[10],
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[CalendarData]:
    """Retrieve the annual marketing calendar with scheduled activities."""
    _ = request
    service = CalendarService(db, settings)
    result = service.get_calendar(user=current_user, year=year, month=month)
    return SuccessResponse(
        success=True,
        message="Marketing calendar retrieved successfully.",
        data=result,
    )
