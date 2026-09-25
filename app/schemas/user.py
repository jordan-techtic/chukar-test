"""Example user schema demonstrating Pydantic validation patterns."""

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Basic user fields for validation examples."""

    username: str = Field(..., description="Unique username.", examples=["marketing_user"])
    email: EmailStr = Field(
        ...,
        description="User email address.",
        examples=["marketing.user@example.com"],
    )
