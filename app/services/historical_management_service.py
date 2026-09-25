"""Business logic for historical calendar comparison."""

from datetime import date

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.exceptions.http_exceptions import ForbiddenError
from app.models.user import User
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import (
    ActivityViewMode,
    HistoricalCalendarEntry,
    HistoricalManagementData,
    KlaviyoPerformanceMetrics,
    ToggleViewData,
)
from app.services.klaviyo_service import KlaviyoService


class HistoricalManagementService:
    """Compares current and previous year marketing calendars."""

    def __init__(
        self,
        db: Session,
        settings: Settings,
        klaviyo_service: KlaviyoService | None = None,
    ) -> None:
        """Initialize with database session and settings."""
        self._settings = settings
        self._repo = ActivityRepository(db)
        self._klaviyo = klaviyo_service or KlaviyoService(settings)

    def get_comparison(
        self,
        user: User,
        reference_year: int | None = None,
        include_performance: bool = False,
    ) -> HistoricalManagementData:
        """Return side-by-side current and previous year calendars with recurring flags."""
        self._ensure_performance_access(include_performance)
        current_year = reference_year or date.today().year
        previous_year = current_year - 1

        current_entries = self._build_calendar_entries(current_year, include_performance)
        previous_entries = self._build_calendar_entries(previous_year, include_performance)
        self._mark_recurring(current_entries, previous_entries)

        return HistoricalManagementData(
            current_year=current_year,
            previous_year=previous_year,
            role=user.role,
            organization=self._settings.organization_name,
            current_calendar=current_entries,
            previous_calendar=previous_entries,
            view="side_by_side",
        )

    def toggle_view(
        self,
        user: User,
        view: ActivityViewMode,
        reference_year: int | None = None,
        include_performance: bool = False,
    ) -> ToggleViewData:
        """Return calendar data filtered by the requested view mode."""
        comparison = self.get_comparison(
            user=user,
            reference_year=reference_year,
            include_performance=include_performance,
        )

        if view == "current":
            return ToggleViewData(
                view=view,
                current_year=comparison.current_year,
                previous_year=comparison.previous_year,
                role=comparison.role,
                organization=comparison.organization,
                current_calendar=comparison.current_calendar,
                previous_calendar=[],
            )
        if view == "historical":
            return ToggleViewData(
                view=view,
                current_year=comparison.current_year,
                previous_year=comparison.previous_year,
                role=comparison.role,
                organization=comparison.organization,
                current_calendar=[],
                previous_calendar=comparison.previous_calendar,
            )

        return ToggleViewData(
            view="side_by_side",
            current_year=comparison.current_year,
            previous_year=comparison.previous_year,
            role=comparison.role,
            organization=comparison.organization,
            current_calendar=comparison.current_calendar,
            previous_calendar=comparison.previous_calendar,
        )

    def _ensure_performance_access(self, include_performance: bool) -> None:
        """Raise when Klaviyo performance is requested without permission."""
        if include_performance and not self._settings.klaviyo_performance_enabled:
            raise ForbiddenError(
                message="You do not have permission to access historical performance data.",
                code="PERFORMANCE_ACCESS_DENIED",
            )

    def _build_calendar_entries(
        self,
        year: int,
        include_performance: bool,
    ) -> list[HistoricalCalendarEntry]:
        """Map stored activities to historical calendar entries for a year."""
        activities = self._repo.list_by_year(year)
        entries: list[HistoricalCalendarEntry] = []
        for activity in activities:
            performance: KlaviyoPerformanceMetrics | None = None
            if include_performance:
                performance = self._klaviyo.get_performance_for_campaign(activity.campaign_code)
            entries.append(
                HistoricalCalendarEntry(
                    activity_date=activity.activity_date,
                    campaign=activity.title,
                    activity_type=activity.activity_type,
                    description=activity.description,
                    campaign_code=activity.campaign_code,
                    is_recurring=False,
                    performance=performance,
                )
            )
        return entries

    def _mark_recurring(
        self,
        current_entries: list[HistoricalCalendarEntry],
        previous_entries: list[HistoricalCalendarEntry],
    ) -> None:
        """Highlight recurring campaigns matching title and month/day across years."""
        previous_keys = {
            (entry.campaign.lower(), entry.activity_date.month, entry.activity_date.day)
            for entry in previous_entries
        }

        for entry in current_entries:
            key = (entry.campaign.lower(), entry.activity_date.month, entry.activity_date.day)
            if key in previous_keys:
                entry.is_recurring = True

        current_keys = {
            (entry.campaign.lower(), entry.activity_date.month, entry.activity_date.day)
            for entry in current_entries
        }

        for entry in previous_entries:
            key = (entry.campaign.lower(), entry.activity_date.month, entry.activity_date.day)
            if key in current_keys:
                entry.is_recurring = True
