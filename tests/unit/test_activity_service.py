"""Unit tests for ActivityService."""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from app.exceptions.http_exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models.activity import Activity
from app.models.user import User
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import CreateActivityRequest, UpdateActivityRequest
from app.services.activity_service import ActivityService


@pytest.fixture
def member_user() -> User:
    """Return a mock marketing team member."""
    user = MagicMock(spec=User)
    user.id = "550e8400-e29b-41d4-a716-446655440000"
    return user


@pytest.fixture
def activity_service() -> tuple[ActivityService, MagicMock]:
    """Return ActivityService with mocked repository."""
    db = MagicMock()
    settings = MagicMock()
    service = ActivityService(db, settings)
    repo = MagicMock(spec=ActivityRepository)
    service._repo = repo
    service._klaviyo = MagicMock()
    return service, repo


def test_create_activity_success(activity_service, member_user) -> None:
    """Create persists a valid activity and returns response."""
    service, repo = activity_service
    repo.get_by_date_and_type.return_value = None
    tomorrow = date.today() + timedelta(days=1)
    payload = CreateActivityRequest(
        activity_type="email_send",
        title="Launch Email",
        activity_date=tomorrow,
    )

    saved = Activity(
        id="660e8400-e29b-41d4-a716-446655440001",
        activity_type="email_send",
        title="Launch Email",
        activity_date=tomorrow,
        campaign_code="C6-MO10-Y25",
        category="promotions",
        status="active",
        version=1,
    )
    repo.create.return_value = saved

    result = service.create(member_user, payload)
    assert result.title == "Launch Email"
    assert result.campaign_code.startswith("C")
    repo.create.assert_called_once()


def test_create_activity_rejects_past_date(activity_service, member_user) -> None:
    """Create rejects dates in the past."""
    service, _repo = activity_service
    payload = CreateActivityRequest(
        activity_type="email_send",
        title="Old Campaign",
        activity_date=date.today() - timedelta(days=1),
    )
    with pytest.raises(BadRequestError) as exc_info:
        service.create(member_user, payload)
    assert exc_info.value.code == "INVALID_ACTIVITY_DATE"


def test_create_activity_rejects_duplicate_type_on_date(activity_service, member_user) -> None:
    """Create rejects duplicate activity type on the same date."""
    service, repo = activity_service
    tomorrow = date.today() + timedelta(days=1)
    repo.get_by_date_and_type.return_value = MagicMock()
    payload = CreateActivityRequest(
        activity_type="email_send",
        title="Duplicate",
        activity_date=tomorrow,
    )
    with pytest.raises(ConflictError) as exc_info:
        service.create(member_user, payload)
    assert exc_info.value.code == "ACTIVITY_TYPE_DATE_CONFLICT"


def test_get_by_id_not_found(activity_service) -> None:
    """Get by ID raises NotFoundError when missing."""
    service, repo = activity_service
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError) as exc_info:
        service.get_by_id("770e8400-e29b-41d4-a716-446655440002")
    assert exc_info.value.code == "ACTIVITY_NOT_FOUND"


def test_get_by_id_performance_access_denied(activity_service) -> None:
    """Performance lookup denied when KLAVIYO_PERFORMANCE_ENABLED is false."""
    service, repo = activity_service
    tomorrow = date.today() + timedelta(days=1)
    activity = Activity(
        id="770e8400-e29b-41d4-a716-446655440003",
        activity_type="email_send",
        title="Launch",
        activity_date=tomorrow,
        campaign_code="C6-MO10-Y25",
        category="promotions",
        status="active",
        version=1,
    )
    service._settings.klaviyo_performance_enabled = False
    repo.get_by_id.return_value = activity
    with pytest.raises(ForbiddenError) as exc_info:
        service.get_by_id(activity.id, include_performance=True)
    assert exc_info.value.code == "PERFORMANCE_ACCESS_DENIED"


def test_update_version_conflict(activity_service) -> None:
    """Update rejects stale version for concurrent edits."""
    service, repo = activity_service
    tomorrow = date.today() + timedelta(days=1)
    activity = Activity(
        id="770e8400-e29b-41d4-a716-446655440002",
        activity_type="email_send",
        title="Launch",
        activity_date=tomorrow,
        campaign_code="C6-MO10-Y25",
        category="promotions",
        status="active",
        version=2,
    )
    repo.get_by_id.return_value = activity
    payload = UpdateActivityRequest(title="Updated", version=1)
    with pytest.raises(ConflictError) as exc_info:
        service.update(activity.id, payload)
    assert exc_info.value.code == "ACTIVITY_VERSION_CONFLICT"
