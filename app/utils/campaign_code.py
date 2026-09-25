"""Campaign code generation utilities."""

from datetime import date

from app.constants.activity_types import ACTIVITY_TYPE_CONFIG, CATEGORY_CODES


def generate_campaign_code(activity_type: str, activity_date: date) -> str:
    """Generate a campaign code in C6-MO6-Y25 format from type and date."""
    category = ACTIVITY_TYPE_CONFIG[activity_type]["category"]
    category_num = CATEGORY_CODES.get(category, 0)
    month = activity_date.month
    year_suffix = activity_date.year % 100
    return f"C{category_num}-MO{month}-Y{year_suffix:02d}"
