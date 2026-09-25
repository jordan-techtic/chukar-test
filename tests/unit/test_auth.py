"""Unit tests for pytest wiring and auth utilities."""

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, create_access_token, decode_token


def test_pytest_wiring_imports_app_security() -> None:
    """Ensure security helpers import successfully."""
    settings = get_settings()
    assert settings.jwt_algorithm == "HS256"


def test_pytest_wiring_jwt_roundtrip() -> None:
    """Ensure JWT access tokens can be created and decoded."""
    settings = get_settings()
    token = create_access_token({"sub": "00000000-0000-0000-0000-000000000001"}, settings)
    payload = decode_token(token, settings)
    assert payload["sub"] == "00000000-0000-0000-0000-000000000001"
    assert payload["type"] == TOKEN_TYPE_ACCESS
