"""Pydantic schemas for marketing team member authentication."""

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials for marketing team member login."""

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
        description="Registered email address or username (case-insensitive).",
        examples=["marketing.user@example.com", "marketing_user"],
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

    id: uuid.UUID = Field(
        ...,
        description="Unique user identifier (UUID).",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    email: EmailStr = Field(
        ...,
        description="Registered email address.",
        examples=["marketing.user@example.com"],
    )
    username: str = Field(
        ...,
        description="Unique username.",
        examples=["marketing_user"],
    )
    role: str = Field(
        ...,
        description="Application role assigned to the user.",
        examples=["marketing_team_member"],
    )


class TokenPair(BaseModel):
    """JWT access and refresh token pair."""

    access_token: str = Field(
        ...,
        description="JWT access token. Send as `Authorization: Bearer <access_token>` on protected routes.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access.example"],
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token issued alongside the access token.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh.example"],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type for the Authorization header.",
        examples=["bearer"],
    )


class LoginData(BaseModel):
    """Successful login payload."""

    tokens: TokenPair = Field(..., description="Issued authentication tokens.")
    user: UserSummary = Field(..., description="Authenticated user summary.")


class ForgotPasswordRequest(BaseModel):
    """Request to initiate password recovery."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"email": "marketing.user@example.com"},
            ]
        }
    )

    email: EmailStr = Field(
        ...,
        description="Registered email address for the account (case-insensitive lookup).",
        examples=["marketing.user@example.com"],
    )


class ForgotPasswordData(BaseModel):
    """Generic forgot-password response payload."""

    message: str = Field(
        ...,
        description="Generic confirmation message (identical for registered and unregistered emails).",
        examples=[
            "If an account exists for this email, a password reset link has been sent.",
        ],
    )
