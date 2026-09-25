"""Integration tests for health check and API documentation."""

from fastapi.testclient import TestClient


def test_get_health_returns_200(client: TestClient) -> None:
    """GET /api/v1/health returns 200 with standard success envelope."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Service is healthy."
    assert body["data"]["status"] == "OK"


def test_swagger_docs_accessible(client: TestClient) -> None:
    """Swagger UI is reachable at /docs."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_accessible(client: TestClient) -> None:
    """OpenAPI JSON schema is reachable at /openapi.json."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Marketing Content Calendar API"
    assert "/api/v1/health" in schema["paths"]
