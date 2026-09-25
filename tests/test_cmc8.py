"""CMC-8 integration tests: project setup, health, OpenAPI, JWT scaffold."""

import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, create_access_token, decode_token
from app.main import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "app/main.py",
    "app/core/config.py",
    "app/core/security.py",
    "app/core/logging.py",
    "app/db/session.py",
    "app/db/base.py",
    "app/db/migrations/env.py",
    "app/exceptions/http_exceptions.py",
    "app/middleware/auth_middleware.py",
    "app/middleware/logging_middleware.py",
    "app/api/v1/router.py",
    "app/api/v1/endpoints/health.py",
    "tests/unit",
    "tests/integration",
    "scripts",
]


def test_cmc8_project_folder_structure_exists() -> None:
    """Project scaffolding should include the standard folder tree."""
    for relative_path in REQUIRED_PATHS:
        assert (PROJECT_ROOT / relative_path).exists(), f"Missing {relative_path}"


def test_cmc8_project_modules_importable() -> None:
    """Core application modules should import without error."""
    modules = [
        "app.main",
        "app.core.config",
        "app.core.security",
        "app.db.session",
        "app.exceptions.http_exceptions",
        "app.api.v1.endpoints.health",
    ]
    for module_name in modules:
        importlib.import_module(module_name)


def test_cmc8_health_returns_200(client: TestClient) -> None:
    """GET /api/v1/health should return HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_cmc8_swagger_docs_reachable(client: TestClient) -> None:
    """Swagger docs should be reachable locally."""
    assert client.get("/docs").status_code == 200


def test_cmc8_openapi_lists_versioned_routes(client: TestClient) -> None:
    """OpenAPI schema should list versioned API routes."""
    schema = client.get("/openapi.json").json()
    assert any(path.startswith("/api/v1/") for path in schema["paths"])


def test_cmc8_jwt_settings_loaded_from_env() -> None:
    """JWT settings should load from environment configuration."""
    settings = get_settings()
    assert settings.jwt_secret
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 7


def test_cmc8_validation_error_uses_standard_envelope() -> None:
    """Validation errors should use the standard error envelope with field details."""

    class DemoRequest(BaseModel):
        """Temporary schema used only to trigger validation in this test."""

        password: str = Field(..., min_length=1, description="Required password field.")

    test_app: FastAPI = create_app()

    @test_app.post("/api/v1/_test/validation")
    async def validation_demo(body: DemoRequest) -> dict[str, bool]:
        return {"ok": True}

    with TestClient(test_app) as validation_client:
        response = validation_client.post("/api/v1/_test/validation", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error."
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert any(item["field"] == "password" for item in body["error"]["details"])


def test_cmc8_login_issues_decodable_jwt_access_token() -> None:
    """JWT scaffold should issue decodable access tokens with type claim."""
    settings = get_settings()
    token = create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000099"},
        settings,
    )
    payload = decode_token(token, settings)
    assert payload["type"] == TOKEN_TYPE_ACCESS
    assert payload["sub"] == "00000000-0000-0000-0000-000000000099"
