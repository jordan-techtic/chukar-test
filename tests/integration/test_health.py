"""Integration tests for health check and API documentation."""

from fastapi.testclient import TestClient


def test_get_health_returns_200(client: TestClient) -> None:
    """GET /api/v1/health should return 200 with OK status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "OK"


def test_swagger_docs_accessible(client: TestClient) -> None:
    """Swagger UI should be reachable."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_accessible(client: TestClient) -> None:
    """OpenAPI schema JSON should be reachable."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/health" in schema["paths"]
