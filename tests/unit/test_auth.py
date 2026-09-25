"""Unit tests for pytest wiring and auth utilities."""

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, create_access_token, decode_token


def test_pytest_wiring_jwt_roundtrip() -> None:
    """Verify pytest collects tests and JWT helpers issue decodable tokens."""
    settings = get_settings()
    token = create_access_token({"sub": "test-user-id"}, settings)
    payload = decode_token(token, settings)
    assert payload["sub"] == "test-user-id"
    assert payload["type"] == TOKEN_TYPE_ACCESS
