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
from app.schemas.responses import ErrorResponse, SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/marketing-team-member", tags=["marketing-team-member"])

_ERROR_RESPONSES = {
    401: {
        "description": "Invalid credentials or missing authentication.",
        "model": ErrorResponse,
    },
    403: {
        "description": "Account inactive or access denied.",
        "model": ErrorResponse,
    },
    422: {
        "description": "Validation error.",
        "model": ErrorResponse,
    },
    429: {
        "description": "Rate limit exceeded.",
        "model": ErrorResponse,
    },
    500: {
        "description": "Internal server error.",
        "model": ErrorResponse,
    },
}


@router.post(
    "/login",
    response_model=SuccessResponse[LoginData],
    status_code=status.HTTP_200_OK,
    summary="Marketing team member login",
    description=(
        "Authenticate a marketing team member using their registered email or "
        "username and password. Returns JWT access and refresh tokens on success. "
        "Access is restricted to active users with the marketing_team_member role."
    ),
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
        **_ERROR_RESPONSES,
    },
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
        "email is sent via Klaviyo. The response is always generic to prevent "
        "email enumeration."
    ),
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
        422: _ERROR_RESPONSES[422],
        429: _ERROR_RESPONSES[429],
        500: _ERROR_RESPONSES[500],
    },
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
