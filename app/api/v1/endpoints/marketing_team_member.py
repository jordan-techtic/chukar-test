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
    ErrorResponse,
    SuccessResponse,
    openapi_error_response,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/marketing-team-member", tags=["marketing-team-member"])

_PUBLIC_SECURITY: list[dict[str, list[str]]] = []

_LOGIN_ERROR_RESPONSES = {
    **openapi_error_response(
        401,
        "Invalid credentials.",
        example=OPENAPI_ERROR_EXAMPLE_INVALID_CREDENTIALS,
    ),
    **openapi_error_response(
        403,
        "Account inactive or role not authorized.",
        examples={
            "account_inactive": {
                "summary": "Inactive account",
                "value": OPENAPI_ERROR_EXAMPLE_ACCOUNT_INACTIVE,
            },
            "access_denied": {
                "summary": "Wrong role",
                "value": OPENAPI_ERROR_EXAMPLE_ACCESS_DENIED,
            },
        },
    ),
    **openapi_error_response(
        422,
        "Request validation failed.",
        example=OPENAPI_ERROR_EXAMPLE_VALIDATION,
    ),
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
}

_FORGOT_PASSWORD_ERROR_RESPONSES = {
    **openapi_error_response(
        422,
        "Request validation failed.",
        example=OPENAPI_ERROR_EXAMPLE_VALIDATION,
    ),
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
}


@router.post(
    "/login",
    response_model=SuccessResponse[LoginData],
    status_code=status.HTTP_200_OK,
    summary="Marketing team member login",
    description=(
        "Authenticate a marketing team member using their registered email or "
        "username and password. On success returns JWT access and refresh tokens "
        "plus a user summary. Access is restricted to active users with the "
        "marketing_team_member role.\n\n"
        "**Authentication:** Public — no Bearer token required.\n\n"
        "**Stable error codes:**\n"
        "- `INVALID_CREDENTIALS` (401) — unknown user or wrong password\n"
        "- `ACCOUNT_INACTIVE` (403) — user exists but is deactivated\n"
        "- `ACCESS_DENIED` (403) — user role is not marketing_team_member\n"
        "- `VALIDATION_ERROR` (422) — missing or invalid request fields\n"
        "- `RATE_LIMIT_EXCEEDED` (429) — too many login attempts\n"
        "- `INTERNAL_SERVER_ERROR` (500) — unexpected server failure"
    ),
    operation_id="marketingTeamMemberLogin",
    responses={
        200: {
            "description": "Login successful.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Login successful.",
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIs...",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                            "token_type": "bearer",
                            "user": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "email": "marketing.user@example.com",
                                "username": "marketing_user",
                                "role": "marketing_team_member",
                            },
                        },
                    }
                }
            },
        },
        **_LOGIN_ERROR_RESPONSES,
    },
    openapi_extra={"security": []},
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SuccessResponse[LoginData]:
    """Authenticate marketing team member and return JWT tokens."""
    auth_service = AuthService(db, settings)
    login_data = auth_service.login(body.email_or_username, body.password)
    return SuccessResponse[LoginData](
        success=True,
        message="Login successful.",
        data=login_data,
    )


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[ForgotPasswordData],
    status_code=status.HTTP_200_OK,
    summary="Initiate password recovery",
    description=(
        "Initiate the forgot-password flow for a registered email address. "
        "If an active marketing team member account exists, a password reset "
        "email is sent via Klaviyo. The HTTP 200 response is always generic "
        "to prevent email enumeration — the same body is returned for unknown, "
        "inactive, or unauthorized emails (no email is sent in those cases).\n\n"
        "**Authentication:** Public — no Bearer token required.\n\n"
        "**Stable error codes:**\n"
        "- `VALIDATION_ERROR` (422) — invalid email format or missing field\n"
        "- `RATE_LIMIT_EXCEEDED` (429) — too many recovery requests\n"
        "- `INTERNAL_SERVER_ERROR` (500) — unexpected server failure"
    ),
    operation_id="marketingTeamMemberForgotPassword",
    responses={
        200: {
            "description": "Password recovery initiated (generic response).",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Password recovery initiated.",
                        "data": {
                            "message": (
                                "If an account exists for this email, "
                                "a password reset link has been sent."
                            ),
                        },
                    }
                }
            },
        },
        **_FORGOT_PASSWORD_ERROR_RESPONSES,
    },
    openapi_extra={"security": []},
)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SuccessResponse[ForgotPasswordData]:
    """Initiate password recovery for a registered email."""
    auth_service = AuthService(db, settings)
    result = auth_service.forgot_password(body.email)
    return SuccessResponse[ForgotPasswordData](
        success=True,
        message="Password recovery initiated.",
        data=result,
    )
