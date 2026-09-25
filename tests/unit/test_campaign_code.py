"""Unit tests for campaign code generation."""

from datetime import date

from app.utils.campaign_code import generate_campaign_code


def test_generate_campaign_code_promotion_format() -> None:
    """Campaign code follows C6-MO6-Y25 format for promotions in June 2025."""
    result = generate_campaign_code("promotion", date(2025, 6, 15))
    assert result == "C6-MO6-Y25"


def test_generate_campaign_code_content_category() -> None:
    """Content activities use category code 3."""
    result = generate_campaign_code("content", date(2026, 3, 1))
    assert result == "C3-MO3-Y26"
