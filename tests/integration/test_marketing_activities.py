"""Integration tests for marketing calendar and activity APIs."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from tests.conftest import LOGIN_URL, MEMBER_EMAIL, TEST_PASSWORD

CALENDAR_URL = "/api/v1/marketing-team-member/calendar"
ACTIVITIES_URL = "/api/v1/marketing-team-member/activities"
HISTORICAL_URL = "/api/v1/marketing-team-member/historical-management"
TOGGLE_VIEW_URL = "/api/v1/marketing-team-member/historical-management/toggle-view"


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


def test_create_activity_success(db_client: TestClient, auth_headers: dict[str, str]) -> None:
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
    assert body["data"]["campaign_code"].startswith("C")


def test_create_activity_duplicate_type_on_date(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-48] Duplicate activity type on same date returns conflict."""
    activity_date = _future_date(10)
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
    assert second.json()["error"]["code"] == "ACTIVITY_TYPE_DATE_CONFLICT"


def test_get_calendar_with_activities(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-42] Calendar returns scheduled activities grouped by date."""
    activity_date = _future_date(14)
    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "content",
            "title": "Blog Post",
            "date": activity_date,
        },
    )
    assert create.status_code == 201

    year = int(activity_date[:4])
    response = db_client.get(
        f"{CALENDAR_URL}?year={year}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["year"] == year
    assert data["role"] == "marketing_team_member"
    assert data["organization"]
    assert len(data["days"]) >= 1
    assert data["days"][0]["activities"][0]["color"]
    assert data["days"][0]["activities"][0]["type"] == "content"


def test_activity_crud_lifecycle(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-42] Activity can be retrieved, updated, and deleted."""
    create = db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "focus",
            "title": "Brand Focus",
            "date": _future_date(21),
        },
    )
    activity_id = create.json()["data"]["id"]
    version = create.json()["data"]["version"]

    get_response = db_client.get(
        f"{ACTIVITIES_URL}/{activity_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200

    update = db_client.put(
        f"{ACTIVITIES_URL}/{activity_id}",
        headers=auth_headers,
        json={"title": "Updated Focus", "version": version},
    )
    assert update.status_code == 200
    assert update.json()["data"]["title"] == "Updated Focus"

    delete = db_client.delete(
        f"{ACTIVITIES_URL}/{activity_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 200


def test_calendar_requires_authentication(db_client: TestClient) -> None:
    """Protected calendar endpoint rejects unauthenticated requests."""
    response = db_client.get(CALENDAR_URL)
    assert response.status_code == 401


def test_historical_management_comparison(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-49] Historical management returns current and previous year calendars."""
    response = db_client.get(HISTORICAL_URL, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "current_calendar" in data
    assert "previous_calendar" in data
    assert data["current_year"] == data["previous_year"] + 1
    assert data["role"] == "marketing_team_member"
    assert data["organization"]


def test_toggle_historical_view(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-49] Toggle view returns filtered calendar data."""
    response = db_client.post(
        TOGGLE_VIEW_URL,
        headers=auth_headers,
        json={"view": "historical"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["view"] == "historical"
    assert data["current_calendar"] == []
    assert data["current_year"] == date.today().year
