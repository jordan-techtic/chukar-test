"""Unit tests for security helpers."""

from datetime import timedelta

import pytest
from jose import JWTError

from app.core.config import get_settings
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_jwt_token,
    verify_password,
)


def test_hash_password_and_verify() -> None:
    """Password hashing and verification should round-trip."""
    hashed = hash_password("SecurePass1!")
    assert verify_password("SecurePass1!", hashed)
    assert not verify_password("WrongPass1!", hashed)


def test_create_access_token_roundtrip() -> None:
    """Access tokens should encode and decode with the access type claim."""
    settings = get_settings()
    token = create_access_token({"sub": "user-1"}, settings)
    payload = decode_token(token, settings)
    assert payload["sub"] == "user-1"
    assert payload["type"] == TOKEN_TYPE_ACCESS


def test_create_refresh_token_has_type_refresh() -> None:
    """Refresh tokens should include the refresh type claim."""
    settings = get_settings()
    token = create_refresh_token({"sub": "user-1"}, settings)
    payload = decode_token(token, settings)
    assert payload["type"] == TOKEN_TYPE_REFRESH


def test_create_access_token_custom_expiry() -> None:
    """Custom expiry deltas should be honored."""
    settings = get_settings()
    token = create_access_token(
        {"sub": "user-1"},
        settings,
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_token(token, settings)
    assert payload["sub"] == "user-1"


def test_decode_token_invalid_raises() -> None:
    """Invalid tokens should raise JWTError on decode."""
    settings = get_settings()
    with pytest.raises(JWTError):
        decode_token("not-a-valid-token", settings)


def test_verify_jwt_token_missing_sub_raises() -> None:
    """Tokens without a subject claim should be rejected."""
    settings = get_settings()
    token = create_access_token({}, settings)
    with pytest.raises(JWTError):
        verify_jwt_token(token, settings, expected_type=TOKEN_TYPE_ACCESS)
