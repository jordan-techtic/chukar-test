"""Unit tests for HistoricalManagementService."""

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest

from app.exceptions.http_exceptions import ForbiddenError
from app.models.activity import Activity
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.services.historical_management_service import HistoricalManagementService


@pytest.fixture
def member_user() -> User:
    """Return a mock marketing team member."""
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.role = MARKETING_TEAM_MEMBER_ROLE
    return user


@pytest.fixture
def historical_service() -> tuple[HistoricalManagementService, MagicMock]:
    """Return HistoricalManagementService with mocked repository."""
    db = MagicMock()
    settings = MagicMock()
    settings.organization_name = "Marketing Content Calendar"
    settings.klaviyo_performance_enabled = False
    service = HistoricalManagementService(db, settings)
    repo = MagicMock()
    service._repo = repo
    service._klaviyo = MagicMock()
    return service, repo


def test_mark_recurring_campaigns_by_title_and_month_day(
    historical_service,
    member_user,
) -> None:
    """Recurring campaigns match title and month/day across years."""
    service, repo = historical_service
    current = [
        Activity(
            id=uuid.uuid4(),
            activity_type="promotion",
            title="New Year Campaign",
            activity_date=date(2025, 1, 1),
            campaign_code="C6-MO1-Y25",
            category="promotions",
            status="active",
            version=1,
            description="New Year promo",
        )
    ]
    previous = [
        Activity(
            id=uuid.uuid4(),
            activity_type="promotion",
            title="New Year Campaign",
            activity_date=date(2024, 1, 1),
            campaign_code="C6-MO1-Y24",
            category="promotions",
            status="active",
            version=1,
            description="New Year promo",
        )
    ]

    repo.list_by_year = MagicMock(side_effect=[current, previous])
    result = service.get_comparison(user=member_user, reference_year=2025)

    assert result.current_calendar[0].is_recurring is True
    assert result.previous_calendar[0].is_recurring is True
    assert result.current_calendar[0].description == "New Year promo"
    assert result.role == MARKETING_TEAM_MEMBER_ROLE
    assert result.organization == "Marketing Content Calendar"


def test_toggle_view_current_only(historical_service, member_user) -> None:
    """Toggle view returns only current year when view is current."""
    service, repo = historical_service
    repo.list_by_year = MagicMock(return_value=[])

    result = service.toggle_view(user=member_user, view="current")
    assert result.view == "current"
    assert result.previous_calendar == []
    assert result.current_year == date.today().year


def test_toggle_view_historical_only(historical_service, member_user) -> None:
    """Toggle view returns only previous year when view is historical."""
    service, repo = historical_service
    repo.list_by_year = MagicMock(return_value=[])

    result = service.toggle_view(user=member_user, view="historical")
    assert result.view == "historical"
    assert result.current_calendar == []


def test_get_comparison_empty_calendars(historical_service, member_user) -> None:
    """Empty years return success with empty calendar arrays."""
    service, repo = historical_service
    repo.list_by_year = MagicMock(return_value=[])

    result = service.get_comparison(user=member_user, reference_year=2099)
    assert result.current_calendar == []
    assert result.previous_calendar == []
    assert result.previous_year == 2098


def test_performance_access_denied(historical_service, member_user) -> None:
    """Performance lookup denied when KLAVIYO_PERFORMANCE_ENABLED is false."""
    service, _repo = historical_service
    service._settings.klaviyo_performance_enabled = False
    with pytest.raises(ForbiddenError) as exc_info:
        service.get_comparison(user=member_user, include_performance=True)
    assert exc_info.value.code == "PERFORMANCE_ACCESS_DENIED"
