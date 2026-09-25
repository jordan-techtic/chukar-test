"""CMC-48 acceptance integration tests: activity creation API."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from tests.conftest import LOGIN_URL, MEMBER_EMAIL, TEST_PASSWORD

ACTIVITIES_URL = "/api/v1/marketing-team-member/activities"
CALENDAR_URL = "/api/v1/marketing-team-member/calendar"


@pytest.fixture
def auth_headers(db_client: TestClient) -> dict[str, str]:
    """Return authorization headers for the marketing team member."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": MEMBER_EMAIL, "password": TEST_PASSWORD},
    )
    token = response.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _future_date(days: int = 7) -> str:
    """Return an ISO date string in the future."""
    return (date.today() + timedelta(days=days)).isoformat()


def test_cmc48_ac_create_activity_success(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-48] Marketing team member can create an activity."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "email_send",
            "title": "Spring Launch",
            "date": _future_date(),
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Spring Launch"
    assert body["data"]["type"] == "email_send"
    assert body["data"]["campaign_code"].startswith("C")
    assert body["data"]["color"].startswith("#")


def test_cmc48_ac_ticket_field_aliases(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-48] Request accepts ticket field names activity_date, details, additional_info."""
    activity_date = _future_date(11)
    response = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "content",
            "title": "Blog Series",
            "activity_date": activity_date,
            "details": "Three-part blog series on product updates.",
            "additional_info": "Coordinate with design team.",
        },
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["date"] == activity_date
    assert data["description"] == "Three-part blog series on product updates."
    assert data["notes"] == "Coordinate with design team."


def test_cmc48_ac_dynamic_required_fields(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-48] Field validation enforces type-specific required fields."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "promotion",
            "title": "Holiday Sale",
            "date": _future_date(12),
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "MISSING_REQUIRED_FIELDS"
    assert "notes" in body["message"].lower() or "additional_info" in body["message"].lower()


def test_cmc48_ac_duplicate_type_on_date(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-48] Prevent submission when same activity type exists on selected date."""
    activity_date = _future_date(13)
    payload = {
        "activity_type": "sms_send",
        "title": "First SMS",
        "date": activity_date,
    }
    first = db_client.post(ACTIVITIES_URL, headers=auth_headers, json=payload)
    assert first.status_code == 201

    second = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={"activity_type": "sms_send", "title": "Second SMS", "date": activity_date},
    )
    assert second.status_code == 409
    body = second.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ACTIVITY_TYPE_DATE_CONFLICT"


def test_cmc48_ac_validation_past_date(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-48] Field validation rejects past activity dates."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "email_send",
            "title": "Past Campaign",
            "date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ACTIVITY_DATE"


def test_cmc48_ac_requires_authentication(db_client: TestClient) -> None:
    """[CMC-48] Activity creation requires authentication."""
    response = db_client.post(
        ACTIVITIES_URL,
        json={"activity_type": "email_send", "title": "No Auth", "date": _future_date()},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_cmc48_ac_frontend_contract_fields(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-48] Create response includes description; errors include stable error code."""
    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "focus",
            "title": "Brand Focus Week",
            "date": _future_date(15),
            "description": "Focus on brand awareness initiatives.",
        },
    )
    assert create.status_code == 201
    assert create.json()["data"]["description"] == "Focus on brand awareness initiatives."

    invalid = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={"activity_type": "invalid_type", "title": "Bad", "date": _future_date(16)},
    )
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
    assert invalid.json()["error"]["details"] is not None


def test_cmc48_ac_activity_type_metadata_for_dynamic_form(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-48] Calendar exposes activity type metadata for dynamic field display."""
    response = db_client.get(CALENDAR_URL, headers=auth_headers)
    assert response.status_code == 200
    types = response.json()["data"]["activity_types"]
    promotion = next(item for item in types if item["activity_type"] == "promotion")
    email = next(item for item in types if item["activity_type"] == "email_send")
    assert "notes" in promotion["required_fields"]
    assert "notes" not in email["required_fields"]
