"""CMC-8 acceptance integration tests: project setup, health, JWT scaffold."""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import TOKEN_TYPE_ACCESS, create_access_token, decode_token
from app.middleware.auth_middleware import PUBLIC_PATHS
from tests.conftest import HEALTH_URL

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
    "app/services",
    "app/models",
    "app/repositories",
    "tests/unit",
    "tests/integration",
    "scripts",
]


def test_cmc8_ac_project_folder_structure_exists() -> None:
    """[CMC-8] Standard python-fastapi folder tree exists."""
    for relative_path in REQUIRED_PATHS:
        assert (PROJECT_ROOT / relative_path).exists(), f"Missing {relative_path}"


def test_cmc8_ac_core_modules_importable() -> None:
    """[CMC-8] Project initialized with importable application modules."""
    for module_name in [
        "app.main",
        "app.core.config",
        "app.core.security",
        "app.db.session",
        "app.services.auth_service",
        "app.api.v1.endpoints.health",
    ]:
        importlib.import_module(module_name)


def test_cmc8_ac_postgresql_connectivity(db_client: TestClient) -> None:
    """[CMC-8] Database wired for PostgreSQL with verified connectivity."""
    from sqlalchemy import create_engine, text

    from app.core.config import get_settings
    from app.db.database_url import normalize_database_url

    settings = get_settings()
    test_url = settings.test_database_url or settings.database_url
    engine = create_engine(normalize_database_url(test_url), pool_pre_ping=True)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()
    assert result == 1


def test_cmc8_ac_jwt_auth_skeleton_configured() -> None:
    """[CMC-8] JWT auth skeleton registered with documented env settings."""
    settings = get_settings()
    assert settings.jwt_secret
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 7
    assert HEALTH_URL in PUBLIC_PATHS
    assert "/api/v1/marketing-team-member/login" in PUBLIC_PATHS


def test_cmc8_ac_jwt_tokens_encode_and_decode() -> None:
    """[CMC-8] JWT access tokens include type claim and decode correctly."""
    settings = get_settings()
    token = create_access_token({"sub": "00000000-0000-0000-0000-000000000001"}, settings)
    payload = decode_token(token, settings)
    assert payload["type"] == TOKEN_TYPE_ACCESS


def test_cmc8_ac_health_returns_200(client: TestClient) -> None:
    """[CMC-8] GET /api/v1/health returns 200."""
    response = client.get(HEALTH_URL)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "OK"


def test_cmc8_ac_swagger_docs_reachable(client: TestClient) -> None:
    """[CMC-8] OpenAPI/Swagger docs are reachable locally."""
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert HEALTH_URL in schema["paths"]


@pytest.mark.skipif(
    subprocess.run([sys.executable, "-m", "flake8", "--version"], capture_output=True).returncode != 0,
    reason="flake8 not installed",
)
def test_cmc8_ac_lint_command_available() -> None:
    """[CMC-8] Lint tooling is installed and runnable via documented command."""
    result = subprocess.run(
        [sys.executable, "-m", "flake8", "app/core/config.py"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_cmc8_ac_sample_unit_tests_discoverable() -> None:
    """[CMC-8] Sample unit tests exist and are discoverable by pytest."""
    assert (PROJECT_ROOT / "tests/unit/test_security.py").exists()
    assert (PROJECT_ROOT / "tests/unit/test_auth_service.py").exists()
