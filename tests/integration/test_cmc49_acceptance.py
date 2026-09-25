"""CMC-49 acceptance integration tests: historical management API."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from tests.conftest import LOGIN_URL, MEMBER_EMAIL, TEST_PASSWORD

HISTORICAL_URL = "/api/v1/marketing-team-member/historical-management"
TOGGLE_VIEW_URL = "/api/v1/marketing-team-member/historical-management/toggle-view"
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


def test_cmc49_ac_side_by_side_comparison(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-49] Users can view both current and previous year calendars side by side."""
    response = db_client.get(HISTORICAL_URL, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "current_calendar" in data
    assert "previous_calendar" in data
    assert data["current_year"] == data["previous_year"] + 1
    assert data["view"] == "side_by_side"
    assert data["role"] == "marketing_team_member"
    assert data["organization"]


def test_cmc49_ac_recurring_campaigns_highlighted(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-49] Recurring campaigns are highlighted when title matches across years."""
    reference_year = date.today().year + 2
    previous_year = reference_year - 1

    db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "promotion",
            "title": "Recurring Holiday Sale",
            "date": f"{reference_year}-03-15",
            "notes": "Spring promo notes",
        },
    )
    db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "email_send",
            "title": "Recurring Holiday Sale",
            "date": f"{previous_year}-03-15",
        },
    )

    response = db_client.get(f"{HISTORICAL_URL}?year={reference_year}", headers=auth_headers)
    data = response.json()["data"]
    current_recurring = [e for e in data["current_calendar"] if e["is_recurring"]]
    previous_recurring = [e for e in data["previous_calendar"] if e["is_recurring"]]
    assert len(current_recurring) >= 1
    assert len(previous_recurring) >= 1


def test_cmc49_ac_toggle_historical_view(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-49] Users can toggle between current and historical views."""
    response = db_client.post(
        TOGGLE_VIEW_URL,
        headers=auth_headers,
        json={"view": "historical"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["view"] == "historical"
    assert data["current_calendar"] == []
    assert "previous_calendar" in data


def test_cmc49_ac_toggle_current_view(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-49] Toggle to current view returns only current year calendar."""
    response = db_client.post(
        TOGGLE_VIEW_URL,
        headers=auth_headers,
        json={"view": "current", "year": date.today().year},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["view"] == "current"
    assert data["previous_calendar"] == []


def test_cmc49_ac_empty_calendars(db_client: TestClient, auth_headers: dict[str, str]) -> None:
    """[CMC-49] Empty historical data returns success with empty arrays."""
    response = db_client.get(f"{HISTORICAL_URL}?year=2098", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["current_calendar"] == []
    assert data["previous_calendar"] == []


def test_cmc49_ac_description_field_in_entries(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-49] Calendar entries include description for frontend detail views."""
    activity_date = _future_date(42)
    db_client.post(
        ACTIVITIES_URL,
        headers=auth_headers,
        json={
            "activity_type": "content",
            "title": "Described Campaign",
            "date": activity_date,
            "description": "Detailed campaign description.",
        },
    )
    year = int(activity_date[:4])
    response = db_client.get(f"{HISTORICAL_URL}?year={year}", headers=auth_headers)
    entry = response.json()["data"]["current_calendar"][0]
    assert entry["description"] == "Detailed campaign description."


def test_cmc49_ac_requires_authentication(db_client: TestClient) -> None:
    """[CMC-49] Historical management requires authentication."""
    response = db_client.get(HISTORICAL_URL)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_cmc49_ac_performance_access_denied(
    db_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """[CMC-49] Klaviyo performance requires explicit server permission."""
    response = db_client.get(
        f"{HISTORICAL_URL}?include_performance=true",
        headers=auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERFORMANCE_ACCESS_DENIED"
