"""OpenAPI examples and documented response maps for marketing calendar APIs."""

from typing import Any

OPENAPI_SUCCESS_EXAMPLE_CREATE_ACTIVITY: dict[str, Any] = {
    "success": True,
    "message": "Marketing activity created successfully.",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "email_send",
        "title": "Spring Launch Campaign",
        "date": "2026-10-15",
        "campaign_code": "C6-MO10-Y26",
        "notes": "Launch email for spring collection.",
        "description": "Primary spring product launch email send.",
        "category": "promotions",
        "status": "active",
        "color": "#4F46E5",
        "version": 1,
        "performance": None,
    },
}

OPENAPI_SUCCESS_EXAMPLE_CALENDAR: dict[str, Any] = {
    "success": True,
    "message": "Marketing calendar retrieved successfully.",
    "data": {
        "year": 2026,
        "month": 10,
        "role": "marketing_team_member",
        "organization": "Marketing Content Calendar",
        "days": [
            {
                "date": "2026-10-15",
                "activities": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "type": "email_send",
                        "title": "Spring Launch Campaign",
                        "date": "2026-10-15",
                        "campaign_code": "C6-MO10-Y26",
                        "notes": None,
                        "description": "Primary spring product launch email send.",
                        "category": "promotions",
                        "status": "active",
                        "color": "#4F46E5",
                        "version": 1,
                        "performance": None,
                    }
                ],
            }
        ],
        "activity_types": [
            {
                "activity_type": "email_send",
                "category": "promotions",
                "required_fields": ["title", "date", "activity_type"],
                "color": "#4F46E5",
            }
        ],
    },
}

OPENAPI_SUCCESS_EXAMPLE_DELETE_ACTIVITY: dict[str, Any] = {
    "success": True,
    "message": "Marketing activity deleted successfully.",
    "data": {"id": "550e8400-e29b-41d4-a716-446655440000"},
}

OPENAPI_ERROR_EXAMPLE_ACTIVITY_NOT_FOUND: dict[str, Any] = {
    "success": False,
    "message": "Marketing activity not found.",
    "error": {"code": "ACTIVITY_NOT_FOUND", "details": None},
}

OPENAPI_ERROR_EXAMPLE_ACTIVITY_TYPE_DATE_CONFLICT: dict[str, Any] = {
    "success": False,
    "message": "An activity of type 'email_send' already exists on 2026-10-15.",
    "error": {"code": "ACTIVITY_TYPE_DATE_CONFLICT", "details": None},
}

OPENAPI_ERROR_EXAMPLE_INVALID_ACTIVITY_DATE: dict[str, Any] = {
    "success": False,
    "message": "Activity date must be today or a future date.",
    "error": {"code": "INVALID_ACTIVITY_DATE", "details": None},
}

OPENAPI_ERROR_EXAMPLE_MISSING_REQUIRED_FIELDS: dict[str, Any] = {
    "success": False,
    "message": "Missing required fields for activity type: notes",
    "error": {"code": "MISSING_REQUIRED_FIELDS", "details": None},
}

OPENAPI_ERROR_EXAMPLE_ACTIVITY_VERSION_CONFLICT: dict[str, Any] = {
    "success": False,
    "message": "Activity was modified by another user. Please refresh and try again.",
    "error": {"code": "ACTIVITY_VERSION_CONFLICT", "details": None},
}

OPENAPI_ERROR_EXAMPLE_PERFORMANCE_ACCESS_DENIED: dict[str, Any] = {
    "success": False,
    "message": "You do not have permission to access historical performance data.",
    "error": {"code": "PERFORMANCE_ACCESS_DENIED", "details": None},
}

OPENAPI_SUCCESS_EXAMPLE_HISTORICAL_MANAGEMENT: dict[str, Any] = {
    "success": True,
    "message": "Historical calendar comparison retrieved successfully.",
    "data": {
        "current_year": 2026,
        "previous_year": 2025,
        "role": "marketing_team_member",
        "organization": "Marketing Content Calendar",
        "view": "side_by_side",
        "current_calendar": [
            {
                "date": "2026-01-01",
                "campaign": "New Year Campaign",
                "activity_type": "promotion",
                "description": "Annual New Year promotion email send.",
                "campaign_code": "C6-MO1-Y26",
                "is_recurring": True,
                "performance": None,
            }
        ],
        "previous_calendar": [
            {
                "date": "2025-01-01",
                "campaign": "New Year Campaign",
                "activity_type": "promotion",
                "description": "Annual New Year promotion email send.",
                "campaign_code": "C6-MO1-Y25",
                "is_recurring": True,
                "performance": None,
            }
        ],
    },
}

OPENAPI_SUCCESS_EXAMPLE_TOGGLE_VIEW: dict[str, Any] = {
    "success": True,
    "message": "Historical calendar view updated successfully.",
    "data": {
        "view": "historical",
        "current_year": 2026,
        "previous_year": 2025,
        "role": "marketing_team_member",
        "organization": "Marketing Content Calendar",
        "current_calendar": [],
        "previous_calendar": [
            {
                "date": "2025-01-01",
                "campaign": "New Year Campaign",
                "activity_type": "promotion",
                "description": "Annual New Year promotion email send.",
                "campaign_code": "C6-MO1-Y25",
                "is_recurring": True,
                "performance": None,
            }
        ],
    },
}
