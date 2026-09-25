"""CMC-42 acceptance integration tests: annual marketing calendar API."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from tests.conftest import LOGIN_URL, MEMBER_EMAIL, TEST_PASSWORD

CALENDAR_URL = "/api/v1/marketing-team-member/calendar"
ACTIVITIES_URL = "/api/v1/marketing-team-member/activities"


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


def test_cmc42_ac_view_annual_calendar(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] User can view the annual marketing calendar."""
    response = db_client.get(f"{CALENDAR_URL}?year={date.today().year}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["year"] == date.today().year
    assert "days" in body["data"]
    assert "activity_types" in body["data"]


def test_cmc42_ac_navigate_month_and_year(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] Users can navigate between months and years via query params."""
    activity_date = _future_date(30)
    month = int(activity_date[5:7])
    year = int(activity_date[:4])

    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={"type": "content", "title": "Nav Test", "date": activity_date},
    )
    assert create.status_code == 201

    by_month = db_client.get(
        f"{CALENDAR_URL}?year={year}&month={month}",
        headers=auth_headers,
    )
    assert by_month.status_code == 200
    assert by_month.json()["data"]["month"] == month


def test_cmc42_ac_colored_activity_entries(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] Activities are displayed with color on scheduled dates."""
    activity_date = _future_date(14)
    db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={"activity_type": "promotion", "title": "Sale", "date": activity_date, "notes": "Required"},
    )
    response = db_client.get(
        f"{CALENDAR_URL}?year={int(activity_date[:4])}",
        headers=auth_headers,
    )
    activity = response.json()["data"]["days"][0]["activities"][0]
    assert activity["color"].startswith("#")
    assert activity["type"] == "promotion"


def test_cmc42_ac_dynamic_activity_type_metadata(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-42] Calendar returns activity type metadata for dynamic forms."""
    response = db_client.get(CALENDAR_URL, headers=auth_headers)
    types = response.json()["data"]["activity_types"]
    assert len(types) >= 1
    assert "required_fields" in types[0]
    assert "color" in types[0]


def test_cmc42_ac_frontend_contract_fields(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] Calendar response includes role, organization, and description fields."""
    activity_date = _future_date(21)
    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "email_send",
            "title": "Contract Test",
            "date": activity_date,
            "description": "Detailed description for frontend.",
        },
    )
    assert create.json()["data"]["description"] == "Detailed description for frontend."

    calendar = db_client.get(CALENDAR_URL, headers=auth_headers)
    data = calendar.json()["data"]
    assert data["role"] == "marketing_team_member"
    assert data["organization"]


def test_cmc42_ac_empty_calendar(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] Empty calendar year returns success with empty days array."""
    response = db_client.get(f"{CALENDAR_URL}?year=2099", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["days"] == []


def test_cmc42_ac_create_validation_past_date(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] Field validation rejects past dates."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "email_send",
            "title": "Past",
            "date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ACTIVITY_DATE"


def test_cmc42_ac_performance_access_denied_by_default(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-42] Historical performance data requires explicit permission."""
    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={"activity_type": "focus", "title": "Perf Test", "date": _future_date(28)},
    )
    activity_id = create.json()["data"]["id"]
    response = db_client.get(
        f"{ACTIVITIES_URL}/{activity_id}?include_performance=true",
        headers=auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERFORMANCE_ACCESS_DENIED"


def test_cmc42_ac_concurrent_edit_version_conflict(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-42] Simultaneous edits return version conflict."""
    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={"activity_type": "sms_send", "title": "Concurrent", "date": _future_date(35)},
    )
    activity_id = create.json()["data"]["id"]
    response = db_client.put(
        f"{ACTIVITIES_URL}/{activity_id}",
        headers=auth_headers,
        json={"title": "Stale Update", "version": 999},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ACTIVITY_VERSION_CONFLICT"
