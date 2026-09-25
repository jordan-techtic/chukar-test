"""Predefined activity types, categories, and validation configuration."""

from typing import TypedDict


class ActivityTypeConfig(TypedDict):
    """Configuration for a single activity type."""

    category: str
    required_fields: list[str]
    color: str


ACTIVITY_CATEGORIES: frozenset[str] = frozenset({"promotions", "content", "focuses"})

ACTIVITY_STATUS_ACTIVE = "active"
ACTIVITY_STATUS_INACTIVE = "inactive"
ACTIVITY_STATUSES: frozenset[str] = frozenset({ACTIVITY_STATUS_ACTIVE, ACTIVITY_STATUS_INACTIVE})

ACTIVITY_TYPE_CONFIG: dict[str, ActivityTypeConfig] = {
    "email_send": {
        "category": "promotions",
        "required_fields": ["title", "date", "activity_type"],
        "color": "#4F46E5",
    },
    "sms_send": {
        "category": "promotions",
        "required_fields": ["title", "date", "activity_type"],
        "color": "#7C3AED",
    },
    "promotion": {
        "category": "promotions",
        "required_fields": ["title", "date", "activity_type", "notes"],
        "color": "#DC2626",
    },
    "content": {
        "category": "content",
        "required_fields": ["title", "date", "activity_type"],
        "color": "#059669",
    },
    "focus": {
        "category": "focuses",
        "required_fields": ["title", "date", "activity_type"],
        "color": "#D97706",
    },
}

CATEGORY_CODES: dict[str, int] = {
    "promotions": 6,
    "content": 3,
    "focuses": 1,
}

CATEGORY_COLORS: dict[str, str] = {
    "promotions": "#DC2626",
    "content": "#059669",
    "focuses": "#D97706",
}
