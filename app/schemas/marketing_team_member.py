"""Pydantic schemas for marketing team member authentication."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request body for marketing team member login."""

    email_or_username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Registered email address or username.",
        examples=["marketing.user@example.com"],
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

    id: str = Field(..., description="User identifier.")
    email: str = Field(..., description="User email address.")
    username: str = Field(..., description="User username.")
    role: str = Field(..., description="User role identifier.")


class LoginData(BaseModel):
    """Token payload returned on successful login."""

    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field(
        default="bearer",
        description="Token type for Authorization header.",
    )
    user: UserSummary = Field(..., description="Authenticated user summary.")


class ForgotPasswordRequest(BaseModel):
    """Request body to initiate password recovery."""

    email: EmailStr = Field(
        ...,
        description="Registered email address for password recovery.",
        examples=["marketing.user@example.com"],
    )


class ForgotPasswordData(BaseModel):
    """Response payload for forgot-password initiation."""

    message: str = Field(
        ...,
        description="Generic confirmation message.",
    )
