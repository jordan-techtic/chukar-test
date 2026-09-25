"""Business logic for marketing activity CRUD operations."""

import uuid
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.constants.activity_types import ACTIVITY_TYPE_CONFIG
from app.core.config import Settings
from app.exceptions.http_exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models.activity import Activity
from app.models.user import User
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import (
    ActivityResponse,
    CreateActivityRequest,
    KlaviyoPerformanceMetrics,
    UpdateActivityRequest,
)
from app.services.klaviyo_service import KlaviyoService
from app.utils.campaign_code import generate_campaign_code


class ActivityService:
    """Handles create, read, update, and delete operations for marketing activities."""

    def __init__(
        self,
        db: Session,
        settings: Settings,
        klaviyo_service: KlaviyoService | None = None,
    ) -> None:
        """Initialize with database session and settings."""
        self._db = db
        self._settings = settings
        self._repo = ActivityRepository(db)
        self._klaviyo = klaviyo_service or KlaviyoService(settings)

    def create(self, user: User, payload: CreateActivityRequest) -> ActivityResponse:
        """Create a new marketing activity with validation and campaign code generation."""
        self._validate_date_not_past(payload.activity_date)
        self._validate_required_fields(payload)

        if self._repo.get_by_date_and_type(payload.activity_date, payload.activity_type):
            raise ConflictError(
                message=(
                    f"An activity of type '{payload.activity_type}' already exists "
                    f"on {payload.activity_date.isoformat()}."
                ),
                code="ACTIVITY_TYPE_DATE_CONFLICT",
            )

        category = ACTIVITY_TYPE_CONFIG[payload.activity_type]["category"]
        activity = Activity(
            activity_type=payload.activity_type,
            title=payload.title.strip(),
            activity_date=payload.activity_date,
            campaign_code=generate_campaign_code(payload.activity_type, payload.activity_date),
            notes=payload.notes,
            description=payload.description,
            category=category,
            status=payload.status,
            created_by=user.id,
        )

        try:
            saved = self._repo.create(activity)
        except IntegrityError as exc:
            raise ConflictError(
                message=(
                    f"An activity of type '{payload.activity_type}' already exists "
                    f"on {payload.activity_date.isoformat()}."
                ),
                code="ACTIVITY_TYPE_DATE_CONFLICT",
            ) from exc

        return self.to_response(saved)

    def get_by_id(
        self,
        activity_id: uuid.UUID,
        include_performance: bool = False,
    ) -> ActivityResponse:
        """Return a single activity by ID."""
        activity = self._repo.get_by_id(activity_id)
        if activity is None:
            raise NotFoundError(
                message="Marketing activity not found.",
                code="ACTIVITY_NOT_FOUND",
            )
        performance = None
        if include_performance:
            if not self._settings.klaviyo_performance_enabled:
                raise ForbiddenError(
                    message="You do not have permission to access historical performance data.",
                    code="PERFORMANCE_ACCESS_DENIED",
                )
            performance = self._klaviyo.get_performance_for_campaign(activity.campaign_code)
        return self.to_response(activity, performance=performance)

    def update(
        self,
        activity_id: uuid.UUID,
        payload: UpdateActivityRequest,
    ) -> ActivityResponse:
        """Update an existing marketing activity."""
        activity = self._repo.get_by_id(activity_id)
        if activity is None:
            raise NotFoundError(
                message="Marketing activity not found.",
                code="ACTIVITY_NOT_FOUND",
            )

        if payload.version is not None and payload.version != activity.version:
            raise ConflictError(
                message="Activity was modified by another user. Please refresh and try again.",
                code="ACTIVITY_VERSION_CONFLICT",
            )

        new_type = payload.activity_type or activity.activity_type
        new_date = payload.activity_date or activity.activity_date

        if payload.activity_date is not None:
            self._validate_date_not_past(payload.activity_date)

        if new_type != activity.activity_type or new_date != activity.activity_date:
            existing = self._repo.get_by_date_and_type(new_date, new_type)
            if existing is not None and existing.id != activity.id:
                raise ConflictError(
                    message=(
                        f"An activity of type '{new_type}' already exists "
                        f"on {new_date.isoformat()}."
                    ),
                    code="ACTIVITY_TYPE_DATE_CONFLICT",
                )

        if payload.activity_type is not None:
            activity.activity_type = payload.activity_type
            activity.category = ACTIVITY_TYPE_CONFIG[payload.activity_type]["category"]
        if payload.title is not None:
            activity.title = payload.title.strip()
        if payload.activity_date is not None:
            activity.activity_date = payload.activity_date
        if payload.notes is not None:
            activity.notes = payload.notes
        if payload.description is not None:
            activity.description = payload.description
        if payload.status is not None:
            activity.status = payload.status

        if payload.activity_type is not None or payload.notes is not None:
            self._validate_required_fields_for_update(activity)

        activity.campaign_code = generate_campaign_code(
            activity.activity_type,
            activity.activity_date,
        )
        activity.version += 1

        try:
            saved = self._repo.update(activity)
        except IntegrityError as exc:
            raise ConflictError(
                message=(
                    f"An activity of type '{new_type}' already exists "
                    f"on {new_date.isoformat()}."
                ),
                code="ACTIVITY_TYPE_DATE_CONFLICT",
            ) from exc

        return self.to_response(saved)

    def delete(self, activity_id: uuid.UUID) -> None:
        """Delete a marketing activity."""
        activity = self._repo.get_by_id(activity_id)
        if activity is None:
            raise NotFoundError(
                message="Marketing activity not found.",
                code="ACTIVITY_NOT_FOUND",
            )
        self._repo.delete(activity)

    def _validate_date_not_past(self, activity_date: date) -> None:
        """Ensure the activity date is today or in the future."""
        today = date.today()
        if activity_date < today:
            raise BadRequestError(
                message="Activity date must be today or a future date.",
                code="INVALID_ACTIVITY_DATE",
            )

    def _validate_required_fields(self, payload: CreateActivityRequest) -> None:
        """Validate required fields based on the selected activity type."""
        self._validate_required_field_values(
            payload.activity_type,
            {
                "title": payload.title,
                "date": payload.activity_date,
                "activity_type": payload.activity_type,
                "notes": payload.notes,
            },
        )

    def _validate_required_fields_for_update(self, activity: Activity) -> None:
        """Validate required fields after applying update values to an activity."""
        self._validate_required_field_values(
            activity.activity_type,
            {
                "title": activity.title,
                "date": activity.activity_date,
                "activity_type": activity.activity_type,
                "notes": activity.notes,
            },
        )

    def _validate_required_field_values(
        self,
        activity_type: str,
        field_values: dict[str, object | None],
    ) -> None:
        """Raise when required fields for an activity type are missing or empty."""
        config = ACTIVITY_TYPE_CONFIG[activity_type]
        missing = [
            field_name
            for field_name in config["required_fields"]
            if field_values.get(field_name) in (None, "")
        ]
        if missing:
            raise BadRequestError(
                message=f"Missing required fields for activity type: {', '.join(missing)}",
                code="MISSING_REQUIRED_FIELDS",
            )

    def to_response(
        self,
        activity: Activity,
        performance: KlaviyoPerformanceMetrics | None = None,
    ) -> ActivityResponse:
        """Map an ORM activity to the API response schema."""
        color = ACTIVITY_TYPE_CONFIG.get(activity.activity_type, {}).get("color", "#6B7280")
        return ActivityResponse(
            id=activity.id,
            activity_type=activity.activity_type,
            title=activity.title,
            activity_date=activity.activity_date,
            campaign_code=activity.campaign_code,
            notes=activity.notes,
            description=activity.description,
            category=activity.category,
            status=activity.status,
            color=color,
            version=activity.version,
            performance=performance,
        )
