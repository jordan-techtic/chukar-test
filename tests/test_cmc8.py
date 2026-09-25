"""CMC-8 integration tests: project setup, health, OpenAPI, JWT scaffold."""

import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, decode_token

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cmc8_project_folder_structure_exists() -> None:
    """CMC-8: Standard folder tree exists at repo root."""
    required_paths = [
        PROJECT_ROOT / "app" / "main.py",
        PROJECT_ROOT / "app" / "api" / "v1" / "router.py",
        PROJECT_ROOT / "app" / "core" / "config.py",
        PROJECT_ROOT / "app" / "core" / "security.py",
        PROJECT_ROOT / "app" / "db" / "session.py",
        PROJECT_ROOT / "app" / "db" / "migrations",
        PROJECT_ROOT / "app" / "models",
        PROJECT_ROOT / "app" / "services",
        PROJECT_ROOT / "app" / "middleware",
        PROJECT_ROOT / "tests",
    ]
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in required_paths if not path.exists()]
    assert missing == [], f"Missing project paths: {missing}"


def test_cmc8_project_modules_importable() -> None:
    """CMC-8: Core application modules are importable."""
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


def test_cmc8_health_returns_200(client: TestClient) -> None:
    """CMC-8: GET /api/v1/health returns 200 with success envelope."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Service is healthy."
    assert body["data"]["status"] == "OK"


def test_cmc8_swagger_docs_reachable(client: TestClient) -> None:
    """CMC-8: OpenAPI/Swagger docs are reachable locally."""
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_cmc8_openapi_lists_versioned_routes(client: TestClient) -> None:
    """CMC-8: OpenAPI schema documents health and auth routes."""
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/marketing-team-member/login" in paths
    assert "/api/v1/marketing-team-member/forgot-password" in paths
    assert schema["info"]["title"] == "Marketing Content Calendar API"


def test_cmc8_jwt_settings_loaded_from_env(settings) -> None:
    """CMC-8: JWT configuration is loaded from environment."""
    assert settings.jwt_secret
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 7


def test_cmc8_login_issues_decodable_jwt_access_token(
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
