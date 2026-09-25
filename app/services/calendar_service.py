"""Business logic for annual marketing calendar views."""

from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.constants.activity_types import ACTIVITY_TYPE_CONFIG
from app.core.config import Settings
from app.exceptions.http_exceptions import BadRequestError
from app.models.user import User
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import (
    ActivityResponse,
    ActivityTypeFieldSchema,
    CalendarData,
    CalendarDayEntry,
)
from app.services.activity_service import ActivityService


class CalendarService:
    """Builds annual calendar payloads from stored marketing activities."""

    def __init__(self, db: Session, settings: Settings) -> None:
        """Initialize with database session and settings."""
        self._settings = settings
        self._repo = ActivityRepository(db)
        self._activity_service = ActivityService(db, settings)

    def get_calendar(
        self,
        user: User,
        year: int | None = None,
        month: int | None = None,
    ) -> CalendarData:
        """Return activities grouped by date for the requested year and optional month."""
        target_year = year or date.today().year
        if month is not None and not 1 <= month <= 12:
            raise BadRequestError(
                message="Month must be between 1 and 12.",
                code="INVALID_CALENDAR_MONTH",
            )

        activities = self._repo.list_by_year(target_year, month=month)
        grouped: dict[date, list[ActivityResponse]] = defaultdict(list)

        for activity in activities:
            response = self._activity_service.to_response(activity)
            grouped[activity.activity_date].append(response)

        days = [
            CalendarDayEntry(activity_date=day, activities=entries)
            for day, entries in sorted(grouped.items())
        ]

        activity_types = [
            ActivityTypeFieldSchema(
                activity_type=type_key,
                category=config["category"],
                required_fields=config["required_fields"],
                color=config["color"],
            )
            for type_key, config in ACTIVITY_TYPE_CONFIG.items()
        ]

        return CalendarData(
            year=target_year,
            month=month,
            role=user.role,
            organization=self._settings.organization_name,
            days=days,
            activity_types=activity_types,
        )
