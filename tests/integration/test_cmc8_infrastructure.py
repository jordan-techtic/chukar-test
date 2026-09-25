"""Integration tests for CMC-8 project setup and infrastructure."""

import importlib

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, decode_token


def test_cmc8_health_returns_200_with_success_envelope(client: TestClient) -> None:
    """CMC-8: GET /api/v1/health returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "OK"


def test_cmc8_swagger_docs_reachable(client: TestClient) -> None:
    """CMC-8: OpenAPI/Swagger docs are reachable locally."""
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_cmc8_openapi_lists_auth_and_health_paths(client: TestClient) -> None:
    """CMC-8: OpenAPI schema documents versioned API routes."""
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/marketing-team-member/login" in paths
    assert "/api/v1/marketing-team-member/forgot-password" in paths


def test_cmc8_project_modules_importable() -> None:
    """CMC-8: Standard folder tree modules are importable."""
    modules = [
        "app.main",
        "app.api.v1.router",
        "app.core.config",
        "app.core.security",
        "app.db.session",
        "app.models.user",
        "app.services.auth_service",
        "app.middleware.auth_middleware",
    ]
    for module_name in modules:
        module = importlib.import_module(module_name)
        assert module is not None


def test_cmc8_jwt_settings_loaded_from_env(settings) -> None:
    """CMC-8: JWT configuration is loaded from environment."""
    assert settings.jwt_secret
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 7


def test_cmc8_login_issues_jwt_access_token(
    db_client: TestClient,
    admin_user,
    mock_klaviyo_client,
) -> None:
    """CMC-8: JWT auth skeleton produces decodable access tokens on login."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": "admin@test.com", "password": "TestAdmin123!"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    payload = decode_token(token, get_settings())
    assert payload["type"] == TOKEN_TYPE_ACCESS
    assert payload["sub"] == str(admin_user.id)


def test_cmc8_validation_error_uses_standard_envelope(db_client: TestClient) -> None:
    """CMC-8: Global validation handler returns structured error envelope."""
    response = db_client.post(
        "/api/v1/marketing-team-member/login",
        json={"email_or_username": "only-field"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
