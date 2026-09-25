"""Historical calendar comparison endpoints."""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.activity import (
    HistoricalManagementData,
    ToggleViewData,
    ToggleViewRequest,
)
from app.schemas.openapi_marketing_calendar import (
    OPENAPI_ERROR_EXAMPLE_PERFORMANCE_ACCESS_DENIED,
    OPENAPI_SUCCESS_EXAMPLE_HISTORICAL_MANAGEMENT,
    OPENAPI_SUCCESS_EXAMPLE_TOGGLE_VIEW,
)
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
from app.services.historical_management_service import HistoricalManagementService

router = APIRouter()

_AUTH_FORBIDDEN_EXAMPLES = {
    "accountInactive": {
        "summary": "Account inactive",
        "value": OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE,
    },
    "accessDenied": {
        "summary": "Wrong role",
        "value": OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED,
    },
}

_COMMON_ERROR_RESPONSES = {
    **openapi_error_response(
        401,
        "Missing or invalid Bearer token.",
        OPENAPI_ERROR_EXAMPLE_UNAUTHORIZED,
    ),
    **openapi_error_response_examples(
        403,
        "Account inactive, wrong role, or performance access denied.",
        {
            **_AUTH_FORBIDDEN_EXAMPLES,
            "performanceDenied": {
                "summary": "Klaviyo performance not permitted",
                "value": OPENAPI_ERROR_EXAMPLE_PERFORMANCE_ACCESS_DENIED,
            },
        },
    ),
    **openapi_error_response(
        422,
        "Request validation failed.",
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

_GET_HISTORICAL_RESPONSES = {
    **openapi_success_response(
        200,
        "Side-by-side current and previous year calendars retrieved.",
        OPENAPI_SUCCESS_EXAMPLE_HISTORICAL_MANAGEMENT,
    ),
    **_COMMON_ERROR_RESPONSES,
}

_TOGGLE_VIEW_RESPONSES = {
    **openapi_success_response(
        200,
        "Historical calendar view toggled successfully.",
        OPENAPI_SUCCESS_EXAMPLE_TOGGLE_VIEW,
    ),
    **_COMMON_ERROR_RESPONSES,
}


@router.get(
    "/historical-management",
    response_model=SuccessResponse[HistoricalManagementData],
    status_code=status.HTTP_200_OK,
    summary="Compare current and previous year calendars",
    operation_id="getHistoricalManagement",
    description=(
        "Retrieve the current year's marketing calendar alongside the previous year's "
        "calendar for side-by-side comparison. Recurring campaigns are flagged with "
        "`is_recurring: true` when the same campaign title appears on the same month "
        "and day across both years.\n\n"
        "**Query parameters:**\n"
        "- `year` — reference year (defaults to current year; previous = year - 1)\n"
        "- `include_performance` — attach Klaviyo metrics per entry when "
        "`KLAVIYO_PERFORMANCE_ENABLED=true`\n\n"
        "**Empty state:** Returns empty `current_calendar` / `previous_calendar` arrays "
        "when no activities exist (HTTP 200).\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Stable error codes:**\n"
        "- `UNAUTHORIZED` (401) — missing or invalid token\n"
        "- `ACCESS_DENIED` (403) — wrong role\n"
        "- `PERFORMANCE_ACCESS_DENIED` (403) — Klaviyo performance not permitted\n"
        "- `VALIDATION_ERROR` (422) — invalid query params\n"
        "- `RATE_LIMIT_EXCEEDED` (429)\n"
        "- `INTERNAL_SERVER_ERROR` (500)"
    ),
    tags=["marketing-team-member"],
    responses=_GET_HISTORICAL_RESPONSES,
)
@limiter.limit("60/minute")
async def get_historical_management(
    request: Request,
    year: int | None = Query(
        default=None,
        ge=2000,
        le=2100,
        description="Reference calendar year (defaults to current year).",
        examples=[2026],
    ),
    include_performance: bool = Query(
        default=False,
        description="Include Klaviyo historical performance metrics when authorized.",
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[HistoricalManagementData]:
    """Retrieve current and previous year marketing calendars for comparison."""
    _ = request
    service = HistoricalManagementService(db, settings)
    result = service.get_comparison(
        user=current_user,
        reference_year=year,
        include_performance=include_performance,
    )
    return SuccessResponse(
        success=True,
        message="Historical calendar comparison retrieved successfully.",
        data=result,
    )


@router.post(
    "/historical-management/toggle-view",
    response_model=SuccessResponse[ToggleViewData],
    status_code=status.HTTP_200_OK,
    summary="Toggle historical calendar view",
    operation_id="toggleHistoricalView",
    description=(
        "Toggle between current-only, historical-only, and side-by-side calendar views.\n\n"
        "**Request body fields:**\n"
        "- `view` — `current`, `historical`, or `side_by_side`\n"
        "- `year` — optional reference year (defaults to current year)\n"
        "- `include_performance` — attach Klaviyo metrics when authorized\n\n"
        "When toggling to `current` or `historical`, the non-selected calendar array "
        "is returned empty. Side-by-side returns both calendars.\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Stable error codes:**\n"
        "- `UNAUTHORIZED` (401) / `ACCESS_DENIED` (403)\n"
        "- `PERFORMANCE_ACCESS_DENIED` (403)\n"
        "- `VALIDATION_ERROR` (422) — invalid view value"
    ),
    tags=["marketing-team-member"],
    responses=_TOGGLE_VIEW_RESPONSES,
)
@limiter.limit("60/minute")
async def toggle_historical_view(
    request: Request,
    body: ToggleViewRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ToggleViewData]:
    """Toggle between current, historical, and side-by-side calendar views."""
    _ = request
    service = HistoricalManagementService(db, settings)
    result = service.toggle_view(
        user=current_user,
        view=body.view,
        reference_year=body.year,
        include_performance=body.include_performance,
    )
    return SuccessResponse(
        success=True,
        message="Historical calendar view updated successfully.",
        data=result,
    )
