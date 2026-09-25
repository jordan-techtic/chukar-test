"""Pydantic schemas for marketing activity and calendar endpoints."""

import uuid
from datetime import date as DateType
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.constants.activity_types import ACTIVITY_STATUSES, ACTIVITY_TYPE_CONFIG

ActivityViewMode = Literal["current", "historical", "side_by_side"]


class ActivityTypeFieldSchema(BaseModel):
    """Metadata describing dynamic fields for an activity type."""

    activity_type: str = Field(..., description="Activity type identifier.")
    category: str = Field(..., description="Category associated with the activity type.")
    required_fields: list[str] = Field(..., description="Required field names for this type.")
    color: str = Field(..., description="Hex color used in calendar display.")


class CreateActivityRequest(BaseModel):
    """Request body for creating a marketing activity."""

    model_config = ConfigDict(populate_by_name=True)

    activity_type: str = Field(
        ...,
        validation_alias=AliasChoices("activity_type", "type"),
        description="Predefined activity type (accepts JSON key 'type' or 'activity_type').",
        examples=["email_send"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Activity title displayed on the calendar.",
        examples=["Spring Launch Campaign"],
    )
    activity_date: DateType = Field(
        ...,
        validation_alias=AliasChoices("date", "activity_date"),
        serialization_alias="date",
        description="Scheduled date (YYYY-MM-DD). Accepts JSON key 'date' or 'activity_date'.",
        examples=["2026-10-15"],
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
        validation_alias=AliasChoices("notes", "additional_info"),
        description="Optional notes or additional information (required for promotion type).",
        examples=["Include discount code SPRING26."],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        validation_alias=AliasChoices("description", "details"),
        description="Optional activity details shown in calendar detail views.",
        examples=["Primary spring product launch email send."],
    )
    status: str = Field(
        default="active",
        description="Activity status: active or inactive.",
        examples=["active"],
    )

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, value: str) -> str:
        """Ensure activity type is one of the predefined options."""
        if value not in ACTIVITY_TYPE_CONFIG:
            raise ValueError(
                f"Invalid activity_type. Must be one of: {', '.join(sorted(ACTIVITY_TYPE_CONFIG))}",
            )
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """Ensure status is active or inactive."""
        if value not in ACTIVITY_STATUSES:
            raise ValueError("status must be 'active' or 'inactive'.")
        return value


class UpdateActivityRequest(BaseModel):
    """Request body for updating a marketing activity."""

    model_config = ConfigDict(populate_by_name=True)

    activity_type: str | None = Field(default=None, description="Predefined activity type.")
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated activity title.",
        examples=["Updated Campaign Title"],
    )
    activity_date: DateType | None = Field(
        default=None,
        alias="date",
        description="Scheduled date (YYYY-MM-DD).",
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Updated notes or additional information.",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Updated activity details.",
    )
    status: str | None = Field(default=None, description="Activity status (active|inactive).")
    version: int | None = Field(
        default=None,
        ge=1,
        description="Expected version for optimistic concurrency control.",
    )

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, value: str | None) -> str | None:
        """Ensure activity type is valid when provided."""
        if value is not None and value not in ACTIVITY_TYPE_CONFIG:
            raise ValueError(
                f"Invalid activity_type. Must be one of: {', '.join(sorted(ACTIVITY_TYPE_CONFIG))}",
            )
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        """Ensure status is valid when provided."""
        if value is not None and value not in ACTIVITY_STATUSES:
            raise ValueError("status must be 'active' or 'inactive'.")
        return value


class KlaviyoPerformanceMetrics(BaseModel):
    """Historical performance metrics retrieved from Klaviyo."""

    revenue: float | None = Field(default=None, description="Total revenue attributed to the campaign.")
    open_rate: float | None = Field(default=None, description="Email open rate (0-1).", examples=[0.42])
    click_rate: float | None = Field(default=None, description="Click-through rate (0-1).", examples=[0.08])
    delivered_orders: int | None = Field(default=None, description="Number of delivered orders.", examples=[120])


class ActivityResponse(BaseModel):
    """Single marketing activity returned to clients."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, ser_json_by_alias=True)

    id: uuid.UUID = Field(..., description="Unique activity identifier.")
    activity_type: str = Field(..., serialization_alias="type", description="Activity type.", examples=["email_send"])
    title: str = Field(..., description="Activity title shown on the calendar.", examples=["Spring Launch Campaign"])
    activity_date: DateType = Field(..., serialization_alias="date", description="Scheduled date (YYYY-MM-DD).")
    campaign_code: str = Field(..., description="Auto-generated campaign code (C6-MO6-Y25 format).", examples=["C6-MO10-Y26"])
    notes: str | None = Field(default=None, description="Optional notes or additional information.")
    description: str | None = Field(
        default=None,
        description="Optional activity description shown in calendar detail views.",
    )
    category: str = Field(..., description="Activity category (promotions, content, focuses).")
    status: str = Field(..., description="Activity status: active or inactive.", examples=["active"])
    color: str = Field(..., description="Hex color for calendar display.", examples=["#4F46E5"])
    version: int = Field(..., ge=1, description="Optimistic lock version for concurrent edits.")
    performance: KlaviyoPerformanceMetrics | None = Field(
        default=None,
        description="Klaviyo historical metrics when include_performance is enabled.",
    )


class CalendarDayEntry(BaseModel):
    """Activities scheduled on a single calendar date."""

    activity_date: DateType = Field(..., serialization_alias="date")
    activities: list[ActivityResponse]


class CalendarData(BaseModel):
    """Annual marketing calendar payload."""

    year: int = Field(..., description="Calendar year being displayed.", examples=[2026])
    month: int | None = Field(default=None, description="Optional month filter (1-12).", examples=[10])
    role: str = Field(
        ...,
        description="Authenticated user's role for frontend access control.",
        examples=["marketing_team_member"],
    )
    organization: str = Field(
        ...,
        description="Organization name for calendar header branding.",
        examples=["Marketing Content Calendar"],
    )
    days: list[CalendarDayEntry] = Field(
        default_factory=list,
        description="Scheduled activities grouped by date (empty when no activities).",
    )
    activity_types: list[ActivityTypeFieldSchema] = Field(
        ...,
        description="Metadata for dynamic activity creation forms by type.",
    )


class HistoricalCalendarEntry(BaseModel):
    """Calendar entry used in historical comparison."""

    model_config = ConfigDict(ser_json_by_alias=True)

    activity_date: DateType = Field(..., serialization_alias="date", description="Scheduled date.")
    campaign: str = Field(..., description="Campaign title.", examples=["New Year Campaign"])
    activity_type: str = Field(..., description="Activity type identifier.", examples=["promotion"])
    description: str | None = Field(
        default=None,
        description="Optional activity description for detail views.",
        examples=["Annual New Year promotion email send."],
    )
    campaign_code: str | None = Field(
        default=None,
        description="Auto-generated campaign code linked to Klaviyo metrics.",
        examples=["C6-MO1-Y26"],
    )
    is_recurring: bool = Field(
        default=False,
        description="True when the same campaign appears in both comparison years.",
    )
    performance: KlaviyoPerformanceMetrics | None = Field(
        default=None,
        description="Klaviyo historical metrics when include_performance is enabled.",
    )


class HistoricalManagementData(BaseModel):
    """Side-by-side current and previous year calendar comparison."""

    current_year: int = Field(..., description="Reference calendar year.", examples=[2026])
    previous_year: int = Field(..., description="Previous calendar year for comparison.", examples=[2025])
    role: str = Field(
        ...,
        description="Authenticated user's role.",
        examples=["marketing_team_member"],
    )
    organization: str = Field(
        ...,
        description="Organization name for UI branding.",
        examples=["Marketing Content Calendar"],
    )
    current_calendar: list[HistoricalCalendarEntry] = Field(
        default_factory=list,
        description="Activities scheduled in the current comparison year.",
    )
    previous_calendar: list[HistoricalCalendarEntry] = Field(
        default_factory=list,
        description="Activities scheduled in the previous comparison year.",
    )
    view: ActivityViewMode = Field(
        default="side_by_side",
        description="Active comparison view mode.",
        examples=["side_by_side"],
    )


class ToggleViewRequest(BaseModel):
    """Request to toggle historical management view mode."""

    view: ActivityViewMode = Field(
        ...,
        description="Desired calendar view: current, historical, or side_by_side.",
        examples=["side_by_side"],
    )
    year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
        description="Optional reference year (defaults to current year).",
        examples=[2026],
    )
    include_performance: bool = Field(
        default=False,
        description="Include Klaviyo performance metrics when authorized.",
    )


class ToggleViewData(BaseModel):
    """Response after toggling historical management view."""

    view: ActivityViewMode = Field(..., description="Active view mode after toggle.")
    current_year: int = Field(..., description="Reference calendar year.", examples=[2026])
    previous_year: int = Field(..., description="Previous comparison year.", examples=[2025])
    role: str = Field(..., description="Authenticated user role.", examples=["marketing_team_member"])
    organization: str = Field(..., description="Organization branding name.")
    current_calendar: list[HistoricalCalendarEntry] = Field(
        default_factory=list,
        description="Activities in the reference year (empty when view filters it out).",
    )
    previous_calendar: list[HistoricalCalendarEntry] = Field(
        default_factory=list,
        description="Activities in the previous year (empty when view filters it out).",
    )
