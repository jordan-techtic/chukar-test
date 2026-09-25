"""Comprehensive integration tests for marketing calendar, activity creation, and historical management APIs.

Covers CMC-42, CMC-48, and CMC-49 acceptance criteria with real PostgreSQL,
HTTP assertions, and mocked third-party Klaviyo calls.
"""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.conftest import (
    ADMIN_EMAIL,
    LOGIN_URL,
    TEST_PASSWORD,
)

CALENDAR_URL = "/api/v1/marketing-team-member/calendar"
ACTIVITIES_URL = "/api/v1/marketing-team-member/activities"
HISTORICAL_URL = "/api/v1/marketing-team-member/historical-management"
TOGGLE_VIEW_URL = "/api/v1/marketing-team-member/historical-management/toggle-view"

DESIGN_AC_SKIP = pytest.mark.skip(reason="Frontend/design acceptance criterion — not verifiable via backend API")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future_date(days: int = 7) -> str:
    """Return an ISO date string in the future."""
    return (date.today() + timedelta(days=days)).isoformat()


def _create_activity(
    client: TestClient,
    headers: dict[str, str],
    *,
    activity_type: str = "email_send",
    title: str = "Test Campaign",
    activity_date: str | None = None,
    **extra: object,
) -> dict:
    """Create an activity and return the parsed JSON body."""
    payload = {
        "activity_type": activity_type,
        "title": title,
        "date": activity_date or _future_date(),
        **extra,
    }
    response = client.post(ACTIVITIES_URL, headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# CMC-42 — Annual Marketing Calendar
# ---------------------------------------------------------------------------


def test_cmc42_user_can_view_entire_year_continuous_calendar(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] User can view the entire year in a continuous calendar format."""
    response = db_client.get(f"{CALENDAR_URL}?year={date.today().year}", headers=member_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["year"] == date.today().year
    assert isinstance(data["days"], list)
    assert isinstance(data["activity_types"], list)


def test_cmc42_navigate_months_and_years_seamlessly(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Users can navigate between months and years seamlessly."""
    activity_date = _future_date(30)
    year, month = int(activity_date[:4]), int(activity_date[5:7])
    _create_activity(db_client, member_auth_headers, activity_type="content", title="Nav", activity_date=activity_date)
    response = db_client.get(f"{CALENDAR_URL}?year={year}&month={month}", headers=member_auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["month"] == month


def test_cmc42_colored_entries_on_scheduled_dates(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Marketing activities are displayed as colored entries on their scheduled dates."""
    activity_date = _future_date(14)
    _create_activity(
        db_client,
        member_auth_headers,
        activity_type="promotion",
        title="Sale",
        activity_date=activity_date,
        notes="Required notes",
    )
    response = db_client.get(f"{CALENDAR_URL}?year={int(activity_date[:4])}", headers=member_auth_headers)
    activity = response.json()["data"]["days"][0]["activities"][0]
    assert activity["color"].startswith("#")
    assert activity["date"] == activity_date


def test_cmc42_view_annual_marketing_calendar(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] View annual marketing calendar."""
    response = db_client.get(CALENDAR_URL, headers=member_auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_cmc42_navigate_between_months_and_years(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Navigate between months and years."""
    response = db_client.get(f"{CALENDAR_URL}?year=2030&month=6", headers=member_auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["year"] == 2030
    assert response.json()["data"]["month"] == 6


def test_cmc42_display_activities_on_scheduled_dates(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Display marketing activities on scheduled dates."""
    activity_date = _future_date(18)
    _create_activity(db_client, member_auth_headers, title="Scheduled", activity_date=activity_date)
    response = db_client.get(f"{CALENDAR_URL}?year={int(activity_date[:4])}", headers=member_auth_headers)
    day = response.json()["data"]["days"][0]
    assert day["date"] == activity_date
    assert len(day["activities"]) >= 1


def test_cmc42_create_marketing_activities(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Create Marketing Activities."""
    body = _create_activity(db_client, member_auth_headers, title="Created Activity")
    assert body["data"]["title"] == "Created Activity"
    assert body["data"]["campaign_code"].startswith("C")


def test_cmc42_dynamic_field_display_by_activity_type(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Dynamic field display based on activity type."""
    types = db_client.get(CALENDAR_URL, headers=member_auth_headers).json()["data"]["activity_types"]
    promotion = next(t for t in types if t["activity_type"] == "promotion")
    assert "notes" in promotion["required_fields"]


def test_cmc42_field_validation_required_information(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Field validation for required information."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "promotion", "title": "No Notes", "date": _future_date(20)},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"


@DESIGN_AC_SKIP
def test_cmc42_function_regions_designed() -> None:
    """[CMC-42] All required function regions for Annual Marketing Calendar are designed."""


@DESIGN_AC_SKIP
def test_cmc42_navigation_primary_content_actions() -> None:
    """[CMC-42] Navigation, primary content, and actions are included where applicable."""


@DESIGN_AC_SKIP
def test_cmc42_primary_action_visible_desktop() -> None:
    """[CMC-42] Primary user action is visible without excessive scrolling on desktop."""


@DESIGN_AC_SKIP
def test_cmc42_responsive_breakpoints() -> None:
    """[CMC-42] Annual Marketing Calendar is designed for desktop, tablet, and mobile breakpoints."""


@DESIGN_AC_SKIP
def test_cmc42_layout_adapts_breakpoints() -> None:
    """[CMC-42] Layout adapts correctly across breakpoints with readable spacing."""


@DESIGN_AC_SKIP
def test_cmc42_touch_targets_mobile() -> None:
    """[CMC-42] Touch targets meet minimum size on mobile."""


@DESIGN_AC_SKIP
def test_cmc42_user_goals_visually_clear() -> None:
    """[CMC-42] User goals for this screen are visually clear from hierarchy and labels."""


@DESIGN_AC_SKIP
def test_cmc42_interactive_feedback_states() -> None:
    """[CMC-42] Interactive elements provide visible feedback (hover, focus, active)."""


def test_cmc42_documented_states_empty_success_error(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Documented states: empty, success, error supported by API contract."""
    empty = db_client.get(f"{CALENDAR_URL}?year=2099", headers=member_auth_headers)
    assert empty.status_code == 200
    assert empty.json()["data"]["days"] == []
    err = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "email_send", "title": "X", "date": "2000-01-01"},
    )
    assert err.status_code == 400
    assert err.json()["error"]["code"] == "INVALID_ACTIVITY_DATE"


def test_cmc42_design_system_colors_via_api(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Design system colors delivered via API hex color on activities."""
    body = _create_activity(db_client, member_auth_headers)
    assert body["data"]["color"].startswith("#")


@DESIGN_AC_SKIP
def test_cmc42_reusable_components() -> None:
    """[CMC-42] Reusable components are applied wherever possible."""


@DESIGN_AC_SKIP
def test_cmc42_accessibility_requirements() -> None:
    """[CMC-42] Accessibility requirements are met (ARIA labels, keyboard navigation, contrast)."""


@DESIGN_AC_SKIP
def test_cmc42_figma_organized() -> None:
    """[CMC-42] Figma files are organized, named, and shareable with engineering."""


@DESIGN_AC_SKIP
def test_cmc42_component_specs_sufficient() -> None:
    """[CMC-42] Component specs and annotations are sufficient for implementation."""


@DESIGN_AC_SKIP
def test_cmc42_stakeholder_review_ready() -> None:
    """[CMC-42] Stakeholder review can proceed without missing screen regions."""


def test_cmc42_annual_calendar_display(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Annual calendar display."""
    response = db_client.get(CALENDAR_URL, headers=member_auth_headers)
    assert "year" in response.json()["data"]


@DESIGN_AC_SKIP
def test_cmc42_week_organization() -> None:
    """[CMC-42] Week organization — frontend renders weeks from date-grouped days[]."""


@DESIGN_AC_SKIP
def test_cmc42_navigation_controls() -> None:
    """[CMC-42] Navigation controls — frontend UI; backend exposes year/month query params."""


def test_cmc42_activity_display(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-42] Activity display."""
    body = _create_activity(db_client, member_auth_headers, title="Display Me")
    get_resp = db_client.get(f"{ACTIVITIES_URL}/{body['data']['id']}", headers=member_auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["title"] == "Display Me"


# Bracketed duplicate CMC-42 design AC (skipped)


@DESIGN_AC_SKIP
def test_cmc42_structure_coverage_function_regions() -> None:
    """[CMC-42][Structure & Coverage] All required function regions designed."""


@DESIGN_AC_SKIP
def test_cmc42_structure_coverage_navigation_content_actions() -> None:
    """[CMC-42][Structure & Coverage] Navigation, primary content, and actions included."""


@DESIGN_AC_SKIP
def test_cmc42_structure_coverage_primary_action_desktop() -> None:
    """[CMC-42][Structure & Coverage] Primary user action visible on desktop."""


@DESIGN_AC_SKIP
def test_cmc42_responsive_design_breakpoints() -> None:
    """[CMC-42][Responsive Design] Desktop, tablet, and mobile breakpoints."""


@DESIGN_AC_SKIP
def test_cmc42_responsive_design_layout_spacing() -> None:
    """[CMC-42][Responsive Design] Layout adapts with readable spacing."""


@DESIGN_AC_SKIP
def test_cmc42_responsive_design_touch_targets() -> None:
    """[CMC-42][Responsive Design] Touch targets meet minimum size on mobile."""


@DESIGN_AC_SKIP
def test_cmc42_usability_user_goals_clear() -> None:
    """[CMC-42][Usability & Interaction] User goals visually clear."""


@DESIGN_AC_SKIP
def test_cmc42_usability_interactive_feedback() -> None:
    """[CMC-42][Usability & Interaction] Interactive feedback on hover/focus/active."""


@DESIGN_AC_SKIP
def test_cmc42_usability_documented_states() -> None:
    """[CMC-42][Usability & Interaction] Documented states: loading, hover, success, empty."""


@DESIGN_AC_SKIP
def test_cmc42_consistency_design_system() -> None:
    """[CMC-42][Consistency & Accessibility] Design follows approved design system."""


@DESIGN_AC_SKIP
def test_cmc42_consistency_reusable_components() -> None:
    """[CMC-42][Consistency & Accessibility] Reusable components applied."""


@DESIGN_AC_SKIP
def test_cmc42_consistency_accessibility() -> None:
    """[CMC-42][Consistency & Accessibility] Accessibility requirements met."""


@DESIGN_AC_SKIP
def test_cmc42_handoff_figma_organized() -> None:
    """[CMC-42][Handoff Readiness] Figma files organized and shareable."""


@DESIGN_AC_SKIP
def test_cmc42_handoff_component_specs() -> None:
    """[CMC-42][Handoff Readiness] Component specs sufficient for implementation."""


@DESIGN_AC_SKIP
def test_cmc42_handoff_stakeholder_review() -> None:
    """[CMC-42][Handoff Readiness] Stakeholder review can proceed."""


# ---------------------------------------------------------------------------
# CMC-49 — Historical Management
# ---------------------------------------------------------------------------


def test_cmc49_side_by_side_calendars(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-49] Users can view both current and previous year calendars side by side."""
    response = db_client.get(HISTORICAL_URL, headers=member_auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["current_year"] == data["previous_year"] + 1
    assert "current_calendar" in data and "previous_calendar" in data


def test_cmc49_recurring_campaigns_highlighted(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-49] Recurring campaigns are highlighted for easy identification."""
    ref_year = date.today().year + 2
    db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "promotion", "title": "Recurring Sale", "date": f"{ref_year}-04-10", "notes": "n"},
    )
    db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "email_send", "title": "Recurring Sale", "date": f"{ref_year - 1}-04-10"},
    )
    data = db_client.get(f"{HISTORICAL_URL}?year={ref_year}", headers=member_auth_headers).json()["data"]
    assert any(e["is_recurring"] for e in data["current_calendar"])


def test_cmc49_toggle_current_and_historical_views(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-49] Users can toggle between current and historical views."""
    historical = db_client.post(TOGGLE_VIEW_URL, headers=member_auth_headers, json={"view": "historical"})
    assert historical.status_code == 200
    assert historical.json()["data"]["view"] == "historical"
    current = db_client.post(TOGGLE_VIEW_URL, headers=member_auth_headers, json={"view": "current"})
    assert current.json()["data"]["previous_calendar"] == []


@DESIGN_AC_SKIP
def test_cmc49_function_regions_designed() -> None:
    """[CMC-49] All required function regions for Historical Management are designed."""


@DESIGN_AC_SKIP
def test_cmc49_navigation_primary_content_actions() -> None:
    """[CMC-49] Navigation, primary content, and actions included."""


@DESIGN_AC_SKIP
def test_cmc49_primary_action_visible_desktop() -> None:
    """[CMC-49] Primary user action visible without excessive scrolling on desktop."""


@DESIGN_AC_SKIP
def test_cmc49_responsive_breakpoints() -> None:
    """[CMC-49] Historical Management designed for desktop, tablet, and mobile."""


@DESIGN_AC_SKIP
def test_cmc49_layout_adapts_breakpoints() -> None:
    """[CMC-49] Layout adapts correctly across breakpoints."""


@DESIGN_AC_SKIP
def test_cmc49_touch_targets_mobile() -> None:
    """[CMC-49] Touch targets meet minimum size on mobile."""


@DESIGN_AC_SKIP
def test_cmc49_user_goals_visually_clear() -> None:
    """[CMC-49] User goals visually clear from hierarchy and labels."""


@DESIGN_AC_SKIP
def test_cmc49_interactive_feedback_states() -> None:
    """[CMC-49] Interactive elements provide visible feedback."""


def test_cmc49_documented_states_empty_success_error(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-49] Empty, success, and error states supported by API."""
    empty = db_client.get(f"{HISTORICAL_URL}?year=2098", headers=member_auth_headers)
    assert empty.status_code == 200
    assert empty.json()["data"]["current_calendar"] == []
    denied = db_client.get(f"{HISTORICAL_URL}?include_performance=true", headers=member_auth_headers)
    assert denied.status_code == 403


@DESIGN_AC_SKIP
def test_cmc49_design_system() -> None:
    """[CMC-49] Design follows the approved design system."""


@DESIGN_AC_SKIP
def test_cmc49_reusable_components() -> None:
    """[CMC-49] Reusable components applied wherever possible."""


@DESIGN_AC_SKIP
def test_cmc49_accessibility() -> None:
    """[CMC-49] Accessibility requirements met."""


@DESIGN_AC_SKIP
def test_cmc49_figma_organized() -> None:
    """[CMC-49] Figma files organized and shareable."""


@DESIGN_AC_SKIP
def test_cmc49_component_specs() -> None:
    """[CMC-49] Component specs and annotations sufficient."""


@DESIGN_AC_SKIP
def test_cmc49_stakeholder_review() -> None:
    """[CMC-49] Stakeholder review can proceed without missing regions."""


# ---------------------------------------------------------------------------
# CMC-48 — Activity Creation
# ---------------------------------------------------------------------------


def test_cmc48_activity_creation_functional(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] Activity creation form is accessible and functional for marketing team members."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "email_send", "title": "Launch", "date": _future_date()},
    )
    assert response.status_code == 201
    assert response.json()["success"] is True


def test_cmc48_dynamic_field_display(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] Dynamic field display adapts based on selected activity type."""
    types = db_client.get(CALENDAR_URL, headers=member_auth_headers).json()["data"]["activity_types"]
    assert any("notes" in t["required_fields"] for t in types)


def test_cmc48_field_validation_required_fields(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] Field validation ensures all required fields are filled."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "promotion", "title": "Sale", "date": _future_date(12)},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "MISSING_REQUIRED_FIELDS"


def test_cmc48_prevent_duplicate_type_on_date(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] Prevent submission if same activity type exists on selected date."""
    d = _future_date(13)
    db_client.post(ACTIVITIES_URL, headers=member_auth_headers, json={"activity_type": "sms_send", "title": "A", "date": d})
    dup = db_client.post(ACTIVITIES_URL, headers=member_auth_headers, json={"activity_type": "sms_send", "title": "B", "date": d})
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "ACTIVITY_TYPE_DATE_CONFLICT"


def test_cmc48_success_response_for_toast(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] Successful submission returns success envelope for frontend toast."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "focus", "title": "Toast Test", "date": _future_date(5)},
    )
    body = response.json()
    assert body["success"] is True
    assert "created successfully" in body["message"].lower()


def test_cmc48_error_response_for_toast(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] Error submission returns error envelope for frontend toast."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "bad_type", "title": "X", "date": _future_date()},
    )
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@DESIGN_AC_SKIP
def test_cmc48_form_labels_screen_readers() -> None:
    """[CMC-48] Ensure all form fields have associated labels for screen readers."""


@DESIGN_AC_SKIP
def test_cmc48_keyboard_navigation() -> None:
    """[CMC-48] Keyboard navigation supported for all interactive elements."""


def test_cmc48_api_documentation_openapi(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """[CMC-48] API documentation reflects Activity Creation API in OpenAPI schema."""
    spec = db_client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/api/v1/marketing-team-member/activities" in paths
    post_op = paths["/api/v1/marketing-team-member/activities"]["post"]
    assert post_op["operationId"] == "createMarketingActivity"
    assert "requestBody" in post_op


# ---------------------------------------------------------------------------
# Endpoint edge cases, errors, auth matrix
# ---------------------------------------------------------------------------


def test_edge_max_title_length(db_client: TestClient, member_auth_headers: dict[str, str]) -> None:
    """Edge: title at max length (100 chars) is accepted."""
    title = "T" * 100
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "content", "title": title, "date": _future_date(22)},
    )
    assert response.status_code == 201
    assert response.json()["data"]["title"] == title


def test_edge_title_over_max_length_rejected(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """Edge: title over 100 chars returns 422 validation error."""
    response = db_client.post(
        ACTIVITIES_URL,
        headers=member_auth_headers,
        json={"activity_type": "content", "title": "T" * 101, "date": _future_date()},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_edge_unicode_title(db_client: TestClient, member_auth_headers: dict[str, str]) -> None:
    """Edge: unicode characters in title are persisted correctly."""
    title = "キャンペーン 🎉"
    body = _create_activity(db_client, member_auth_headers, title=title, activity_type="content")
    assert body["data"]["title"] == title


def test_error_activity_not_found(db_client: TestClient, member_auth_headers: dict[str, str]) -> None:
    """Error: GET non-existent activity returns 404 ACTIVITY_NOT_FOUND."""
    missing_id = str(uuid4())
    response = db_client.get(f"{ACTIVITIES_URL}/{missing_id}", headers=member_auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ACTIVITY_NOT_FOUND"


def test_error_delete_not_found(db_client: TestClient, member_auth_headers: dict[str, str]) -> None:
    """Error: DELETE non-existent activity returns 404."""
    response = db_client.delete(f"{ACTIVITIES_URL}/{uuid4()}", headers=member_auth_headers)
    assert response.status_code == 404


def test_auth_missing_token_returns_401(db_client: TestClient) -> None:
    """Auth: missing Bearer token returns 401 on protected calendar endpoint."""
    assert db_client.get(CALENDAR_URL).status_code == 401


def test_auth_expired_token_returns_401(
    db_client: TestClient, expired_access_token: str
) -> None:
    """Auth: expired JWT returns 401."""
    headers = {"Authorization": f"Bearer {expired_access_token}"}
    assert db_client.get(CALENDAR_URL, headers=headers).status_code == 401


def test_auth_viewer_role_denied(
    db_client: TestClient, viewer_auth_headers: dict[str, str]
) -> None:
    """Auth: viewer role receives 403 ACCESS_DENIED on calendar."""
    response = db_client.get(CALENDAR_URL, headers=viewer_auth_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCESS_DENIED"


def test_auth_inactive_member_denied(
    db_client: TestClient, inactive_member_auth_headers: dict[str, str]
) -> None:
    """Auth: inactive marketing member receives 403 ACCOUNT_INACTIVE."""
    response = db_client.get(CALENDAR_URL, headers=inactive_member_auth_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ACCOUNT_INACTIVE"


def test_auth_admin_login_denied(db_client: TestClient) -> None:
    """Auth: admin user cannot login to marketing team member portal."""
    response = db_client.post(
        LOGIN_URL,
        json={"email_or_username": ADMIN_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403


def test_klaviyo_performance_mocked_when_enabled(
    db_client: TestClient,
    member_auth_headers: dict[str, str],
    klaviyo_performance_enabled: None,
) -> None:
    """Klaviyo performance is mocked and returns metrics when feature flag enabled."""
    body = _create_activity(db_client, member_auth_headers, title="Perf Campaign")
    activity_id = body["data"]["id"]
    response = db_client.get(
        f"{ACTIVITIES_URL}/{activity_id}?include_performance=true",
        headers=member_auth_headers,
    )
    assert response.status_code == 200
    perf = response.json()["data"]["performance"]
    assert perf is not None
    assert perf["open_rate"] == 0.42


def test_activity_crud_update_and_delete(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """Happy path: full activity update and delete lifecycle."""
    created = _create_activity(db_client, member_auth_headers, activity_type="focus", title="Lifecycle")
    activity_id = created["data"]["id"]
    version = created["data"]["version"]
    updated = db_client.put(
        f"{ACTIVITIES_URL}/{activity_id}",
        headers=member_auth_headers,
        json={"title": "Updated Lifecycle", "version": version},
    )
    assert updated.status_code == 200
    deleted = db_client.delete(f"{ACTIVITIES_URL}/{activity_id}", headers=member_auth_headers)
    assert deleted.status_code == 200
    assert db_client.get(f"{ACTIVITIES_URL}/{activity_id}", headers=member_auth_headers).status_code == 404


def test_historical_toggle_invalid_view_422(
    db_client: TestClient, member_auth_headers: dict[str, str]
) -> None:
    """Error: invalid toggle view value returns 422 VALIDATION_ERROR."""
    response = db_client.post(
        TOGGLE_VIEW_URL,
        headers=member_auth_headers,
        json={"view": "invalid_mode"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
