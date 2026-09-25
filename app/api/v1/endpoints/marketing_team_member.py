"""Marketing team member authentication endpoints."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.marketing_team_member import (
    ForgotPasswordData,
    ForgotPasswordRequest,
    LoginData,
    LoginRequest,
)
from app.schemas.responses import (
    OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED,
    OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE,
    OPENAPI_ERROR_EXAMPLE_INTERNAL,
    OPENAPI_ERROR_EXAMPLE_INVALID_CREDENTIALS,
    OPENAPI_ERROR_EXAMPLE_RATE_LIMIT,
    OPENAPI_ERROR_EXAMPLE_VALIDATION,
    OPENAPI_SUCCESS_EXAMPLE_FORGOT_PASSWORD,
    OPENAPI_SUCCESS_EXAMPLE_LOGIN,
    SuccessResponse,
    openapi_error_response,
    openapi_error_response_examples,
    openapi_success_response,
)
from app.services.auth_service import AuthService

router = APIRouter()

_LOGIN_FORBIDDEN_EXAMPLES = {
    "accountInactive": {
        "summary": "Account inactive",
        "value": OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE,
    },
    "accessDenied": {
        "summary": "Wrong role",
        "value": OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED,
    },
}

_LOGIN_RESPONSES = {
    **openapi_success_response(
        200,
        "Login successful; returns JWT access/refresh tokens and user summary.",
        OPENAPI_SUCCESS_EXAMPLE_LOGIN,
    ),
    **openapi_error_response(
        401,
        "Invalid credentials.",
        OPENAPI_ERROR_EXAMPLE_INVALID_CREDENTIALS,
    ),
    **openapi_error_response_examples(
        403,
        "Account inactive or role not authorized.",
        _LOGIN_FORBIDDEN_EXAMPLES,
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

_FORGOT_PASSWORD_RESPONSES = {
    **openapi_success_response(
        200,
        "Generic success message (same for registered and unregistered emails).",
        OPENAPI_SUCCESS_EXAMPLE_FORGOT_PASSWORD,
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


@router.post(
    "/login",
    response_model=SuccessResponse[LoginData],
    status_code=status.HTTP_200_OK,
    summary="Marketing team member login",
    operation_id="marketingTeamMemberLogin",
    description=(
        "Authenticate a marketing team member using their registered email or username "
        "and password. On success returns JWT access and refresh tokens plus a user summary. "
        "Access is restricted to active users with the `marketing_team_member` role.\n\n"
        "**Authentication:** Public — no Bearer token required.\n\n"
        "**Rate limit:** 10 requests per minute per client IP.\n\n"
        "**Stable error codes:**\n"
        "- `INVALID_CREDENTIALS` (401) — unknown user or wrong password\n"
        "- `ACCOUNT_INACTIVE` (403) — user exists but is deactivated\n"
        "- `ACCESS_DENIED` (403) — user role is not marketing_team_member\n"
        "- `VALIDATION_ERROR` (422) — missing or invalid request fields\n"
        "- `RATE_LIMIT_EXCEEDED` (429) — too many login attempts\n"
        "- `INTERNAL_SERVER_ERROR` (500) — unexpected server failure"
    ),
    tags=["marketing-team-member"],
    responses=_LOGIN_RESPONSES,
    openapi_extra={"security": []},
)
@limiter.limit("10/minute")
async def marketing_team_member_login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SuccessResponse[LoginData]:
    """Authenticate a marketing team member and return JWT tokens."""
    _ = request
    auth_service = AuthService(db, settings)
    result = auth_service.login(body.email_or_username, body.password)
    return SuccessResponse(
        success=True,
        message="Login successful.",
        data=result,
    )


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[ForgotPasswordData],
    status_code=status.HTTP_200_OK,
    summary="Initiate password recovery",
    operation_id="marketingTeamMemberForgotPassword",
    description=(
        "Initiate the password recovery process for a registered email address. "
        "Always returns the same generic success message whether or not the email "
        "is registered to prevent account enumeration.\n\n"
        "**Authentication:** Public — no Bearer token required.\n\n"
        "**Rate limit:** 10 requests per minute per client IP.\n\n"
        "When a matching active marketing team member exists, a reset token is stored "
        "and a Klaviyo event is dispatched to trigger the password reset email.\n\n"
        "**Stable error codes:**\n"
        "- `VALIDATION_ERROR` (422) — invalid or missing email format\n"
        "- `RATE_LIMIT_EXCEEDED` (429) — too many recovery attempts\n"
        "- `INTERNAL_SERVER_ERROR` (500) — unexpected server failure"
    ),
    tags=["marketing-team-member"],
    responses=_FORGOT_PASSWORD_RESPONSES,
    openapi_extra={"security": []},
)
@limiter.limit("10/minute")
async def marketing_team_member_forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SuccessResponse[ForgotPasswordData]:
    """Initiate password recovery for a marketing team member."""
    _ = request
    auth_service = AuthService(db, settings)
    result = auth_service.forgot_password(body.email)
    return SuccessResponse(
        success=True,
        message=result.message,
        data=result,
    )
