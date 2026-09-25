"""Marketing activity CRUD endpoints."""

import uuid

from fastapi import APIRouter, Depends, Path, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.activity import (
    ActivityResponse,
    CreateActivityRequest,
    UpdateActivityRequest,
)
from app.schemas.openapi_marketing_calendar import (
    OPENAPI_ERROR_EXAMPLE_ACTIVITY_NOT_FOUND,
    OPENAPI_ERROR_EXAMPLE_ACTIVITY_TYPE_DATE_CONFLICT,
    OPENAPI_ERROR_EXAMPLE_ACTIVITY_VERSION_CONFLICT,
    OPENAPI_ERROR_EXAMPLE_INVALID_ACTIVITY_DATE,
    OPENAPI_ERROR_EXAMPLE_MISSING_REQUIRED_FIELDS,
    OPENAPI_ERROR_EXAMPLE_PERFORMANCE_ACCESS_DENIED,
    OPENAPI_SUCCESS_EXAMPLE_CREATE_ACTIVITY,
    OPENAPI_SUCCESS_EXAMPLE_DELETE_ACTIVITY,
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
from app.services.activity_service import ActivityService

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
        "Account inactive or role not authorized.",
        _AUTH_FORBIDDEN_EXAMPLES,
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

_CREATE_RESPONSES = {
    **openapi_success_response(
        201,
        "Marketing activity created successfully.",
        OPENAPI_SUCCESS_EXAMPLE_CREATE_ACTIVITY,
    ),
    **openapi_error_response_examples(
        400,
        "Invalid activity date or missing required fields.",
        {
            "invalidDate": {
                "summary": "Date in the past",
                "value": OPENAPI_ERROR_EXAMPLE_INVALID_ACTIVITY_DATE,
            },
            "missingFields": {
                "summary": "Type-specific required fields missing",
                "value": OPENAPI_ERROR_EXAMPLE_MISSING_REQUIRED_FIELDS,
            },
        },
    ),
    **openapi_error_response(
        409,
        "Duplicate activity type on the same date.",
        OPENAPI_ERROR_EXAMPLE_ACTIVITY_TYPE_DATE_CONFLICT,
    ),
    **_COMMON_ERROR_RESPONSES,
}

_GET_RESPONSES = {
    **openapi_success_response(
        200,
        "Marketing activity retrieved successfully.",
        OPENAPI_SUCCESS_EXAMPLE_CREATE_ACTIVITY,
    ),
    **openapi_error_response(
        403,
        "Historical performance access denied.",
        OPENAPI_ERROR_EXAMPLE_PERFORMANCE_ACCESS_DENIED,
    ),
    **openapi_error_response(
        404,
        "Activity not found.",
        OPENAPI_ERROR_EXAMPLE_ACTIVITY_NOT_FOUND,
    ),
    **_COMMON_ERROR_RESPONSES,
}

_UPDATE_RESPONSES = {
    **openapi_success_response(
        200,
        "Marketing activity updated successfully.",
        OPENAPI_SUCCESS_EXAMPLE_CREATE_ACTIVITY,
    ),
    **openapi_error_response_examples(
        400,
        "Invalid activity date or missing required fields.",
        {
            "missingFields": {
                "summary": "Type-specific required fields missing",
                "value": OPENAPI_ERROR_EXAMPLE_MISSING_REQUIRED_FIELDS,
            },
            "invalidDate": {
                "summary": "Date in the past",
                "value": OPENAPI_ERROR_EXAMPLE_INVALID_ACTIVITY_DATE,
            },
        },
    ),
    **openapi_error_response(
        404,
        "Activity not found.",
        OPENAPI_ERROR_EXAMPLE_ACTIVITY_NOT_FOUND,
    ),
    **openapi_error_response_examples(
        409,
        "Version conflict or duplicate type on date.",
        {
            "versionConflict": {
                "summary": "Stale optimistic lock version",
                "value": OPENAPI_ERROR_EXAMPLE_ACTIVITY_VERSION_CONFLICT,
            },
            "typeDateConflict": {
                "summary": "Duplicate activity type on target date",
                "value": OPENAPI_ERROR_EXAMPLE_ACTIVITY_TYPE_DATE_CONFLICT,
            },
        },
    ),
    **_COMMON_ERROR_RESPONSES,
}

_DELETE_RESPONSES = {
    **openapi_success_response(
        200,
        "Marketing activity deleted successfully.",
        OPENAPI_SUCCESS_EXAMPLE_DELETE_ACTIVITY,
    ),
    **openapi_error_response(
        404,
        "Activity not found.",
        OPENAPI_ERROR_EXAMPLE_ACTIVITY_NOT_FOUND,
    ),
    **_COMMON_ERROR_RESPONSES,
}


@router.post(
    "/activities",
    response_model=SuccessResponse[ActivityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create marketing activity",
    operation_id="createMarketingActivity",
    description=(
        "Create a new marketing activity with dynamic field validation based on activity type. "
        "Campaign code is auto-generated in C6-MO6-Y25 format.\n\n"
        "**Request body fields:**\n"
        "- `type` / `activity_type` — predefined type (email_send, sms_send, promotion, content, focus)\n"
        "- `title` — required, max 100 characters\n"
        "- `date` / `activity_date` — required, YYYY-MM-DD, must be today or future\n"
        "- `notes` / `additional_info` — optional, max 500 characters (required for promotion type)\n"
        "- `description` / `details` — optional, max 500 characters\n"
        "- `status` — active or inactive (default: active)\n\n"
        "Required fields vary by activity type; fetch `GET /calendar` `activity_types` metadata "
        "for dynamic form configuration.\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Stable error codes:**\n"
        "- `INVALID_ACTIVITY_DATE` (400) — date in the past\n"
        "- `MISSING_REQUIRED_FIELDS` (400) — type-specific required fields missing\n"
        "- `ACTIVITY_TYPE_DATE_CONFLICT` (409) — duplicate type on same date\n"
        "- `VALIDATION_ERROR` (422) — invalid request body\n"
        "- `UNAUTHORIZED` (401) / `ACCESS_DENIED` (403) — auth failures"
    ),
    tags=["marketing-team-member"],
    responses=_CREATE_RESPONSES,
)
@limiter.limit("30/minute")
async def create_activity(
    request: Request,
    body: CreateActivityRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ActivityResponse]:
    """Create a new marketing activity with type-based validation."""
    _ = request
    service = ActivityService(db, settings)
    result = service.create(current_user, body)
    return SuccessResponse(
        success=True,
        message="Marketing activity created successfully.",
        data=result,
    )


@router.get(
    "/activities/{activity_id}",
    response_model=SuccessResponse[ActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get marketing activity",
    operation_id="getMarketingActivity",
    description=(
        "Retrieve details of a specific marketing activity by UUID.\n\n"
        "Set `include_performance=true` to attach Klaviyo historical metrics "
        "(requires `KLAVIYO_PERFORMANCE_ENABLED=true` in server config).\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Stable error codes:**\n"
        "- `ACTIVITY_NOT_FOUND` (404)\n"
        "- `PERFORMANCE_ACCESS_DENIED` (403) — Klaviyo performance not permitted\n"
        "- `UNAUTHORIZED` (401) / `ACCESS_DENIED` (403)"
    ),
    tags=["marketing-team-member"],
    responses=_GET_RESPONSES,
)
@limiter.limit("60/minute")
async def get_activity(
    request: Request,
    activity_id: uuid.UUID = Path(
        ...,
        description="UUID of the marketing activity.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    include_performance: bool = Query(
        default=False,
        description="Include Klaviyo historical performance metrics when authorized.",
        examples=[False],
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ActivityResponse]:
    """Retrieve details of a specific marketing activity."""
    _ = request
    _ = current_user
    service = ActivityService(db, settings)
    result = service.get_by_id(activity_id, include_performance=include_performance)
    return SuccessResponse(
        success=True,
        message="Marketing activity retrieved successfully.",
        data=result,
    )


@router.put(
    "/activities/{activity_id}",
    response_model=SuccessResponse[ActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Update marketing activity",
    operation_id="updateMarketingActivity",
    description=(
        "Update an existing marketing activity. Send `version` for optimistic concurrency "
        "control to handle simultaneous edits.\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Stable error codes:**\n"
        "- `ACTIVITY_NOT_FOUND` (404)\n"
        "- `ACTIVITY_VERSION_CONFLICT` (409) — stale version for concurrent edit\n"
        "- `ACTIVITY_TYPE_DATE_CONFLICT` (409) — duplicate type on target date\n"
        "- `INVALID_ACTIVITY_DATE` (400) — date in the past\n"
        "- `MISSING_REQUIRED_FIELDS` (400) — type-specific validation failure"
    ),
    tags=["marketing-team-member"],
    responses=_UPDATE_RESPONSES,
)
@limiter.limit("30/minute")
async def update_activity(
    request: Request,
    body: UpdateActivityRequest,
    activity_id: uuid.UUID = Path(
        ...,
        description="UUID of the marketing activity.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[ActivityResponse]:
    """Update an existing marketing activity."""
    _ = request
    _ = current_user
    service = ActivityService(db, settings)
    result = service.update(activity_id, body)
    return SuccessResponse(
        success=True,
        message="Marketing activity updated successfully.",
        data=result,
    )


@router.delete(
    "/activities/{activity_id}",
    response_model=SuccessResponse[dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Delete marketing activity",
    operation_id="deleteMarketingActivity",
    description=(
        "Delete a marketing activity by UUID.\n\n"
        "**Authentication:** Bearer JWT required (`marketing_team_member` role).\n\n"
        "**Stable error codes:**\n"
        "- `ACTIVITY_NOT_FOUND` (404)\n"
        "- `UNAUTHORIZED` (401) / `ACCESS_DENIED` (403)"
    ),
    tags=["marketing-team-member"],
    responses=_DELETE_RESPONSES,
)
@limiter.limit("30/minute")
async def delete_activity(
    request: Request,
    activity_id: uuid.UUID = Path(
        ...,
        description="UUID of the marketing activity to delete.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[dict[str, str]]:
    """Delete a marketing activity."""
    _ = request
    _ = current_user
    service = ActivityService(db, settings)
    service.delete(activity_id)
    return SuccessResponse(
        success=True,
        message="Marketing activity deleted successfully.",
        data={"id": str(activity_id)},
    )
