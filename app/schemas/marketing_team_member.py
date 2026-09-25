"""Pydantic schemas for marketing team member authentication."""

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials for marketing team member login."""

    email_or_username: str = Field(
        ...,
        min_length=1,
        description="Registered email address or username.",
        examples=["marketing.user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Account password.",
        examples=["SecurePass1!"],
    )


class UserSummary(BaseModel):
    """Public user profile returned after successful login."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique user identifier.")
    email: EmailStr = Field(..., description="Registered email address.")
    username: str = Field(..., description="Unique username.")
    role: str = Field(..., description="Application role.", examples=["marketing_team_member"])


class TokenPair(BaseModel):
    """JWT access and refresh token pair."""

    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field(default="bearer", description="Token type for Authorization header.")


class LoginData(BaseModel):
    """Successful login payload."""

    tokens: TokenPair = Field(..., description="Issued authentication tokens.")
    user: UserSummary = Field(..., description="Authenticated user summary.")


class ForgotPasswordRequest(BaseModel):
    """Request to initiate password recovery."""

    email: EmailStr = Field(
        ...,
        description="Registered email address for the account.",
        examples=["marketing.user@example.com"],
    )


class ForgotPasswordData(BaseModel):
    """Generic forgot-password response payload."""

    message: str = Field(
        ...,
        description="Generic confirmation message (same for registered and unregistered emails).",
    )
