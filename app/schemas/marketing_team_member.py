"""Pydantic schemas for marketing team member authentication."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Request body for marketing team member login."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email_or_username": "marketing.user@example.com",
                    "password": "SecurePass1!",
                },
                {
                    "email_or_username": "marketing_user",
                    "password": "SecurePass1!",
                },
            ]
        }
    )

    email_or_username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description=(
            "Registered email address or username. Lookup is case-insensitive."
        ),
        examples=["marketing.user@example.com", "marketing_user"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Account password.",
        examples=["SecurePass1!"],
    )


class UserSummary(BaseModel):
    """Public user profile returned after successful login."""

    id: str = Field(
        ...,
        description="User UUID.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    email: str = Field(
        ...,
        description="User email address.",
        examples=["marketing.user@example.com"],
    )
    username: str = Field(
        ...,
        description="User username.",
        examples=["marketing_user"],
    )
    role: str = Field(
        ...,
        description="User role identifier.",
        examples=["marketing_team_member"],
    )


class LoginData(BaseModel):
    """Token payload returned on successful login."""

    access_token: str = Field(
        ...,
        description="JWT access token. Pass as Authorization: Bearer <token>.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token for obtaining a new access token.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type for Authorization header.",
        examples=["bearer"],
    )
    user: UserSummary = Field(..., description="Authenticated user summary.")


class ForgotPasswordRequest(BaseModel):
    """Request body to initiate password recovery."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"email": "marketing.user@example.com"},
            ]
        }
    )

    email: EmailStr = Field(
        ...,
        description="Registered email address for password recovery.",
        examples=["marketing.user@example.com"],
    )


class ForgotPasswordData(BaseModel):
    """Response payload for forgot-password initiation."""

    message: str = Field(
        ...,
        description="Generic confirmation message (same for registered and unknown emails).",
        examples=[
            "If an account exists for this email, a password reset link has been sent."
        ],
    )
