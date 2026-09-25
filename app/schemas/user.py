"""Example user schema demonstrating Pydantic validation patterns."""

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields for request validation examples."""

    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique username for the user.",
        examples=["marketing_user"],
    )
    email: EmailStr = Field(
        ...,
        description="User email address.",
        examples=["user@example.com"],
    )
