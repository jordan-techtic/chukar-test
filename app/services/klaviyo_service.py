"""Klaviyo integration service for campaign performance data."""

from app.clients.klaviyo_client import KlaviyoClient, KlaviyoClientError
from app.core.config import Settings
from app.core.logging import logger
from app.schemas.activity import KlaviyoPerformanceMetrics


class KlaviyoService:
    """Encapsulates Klaviyo campaign performance retrieval."""

    def __init__(
        self,
        settings: Settings,
        klaviyo_client: KlaviyoClient | None = None,
    ) -> None:
        """Initialize with settings and optional client override for testing."""
        self._settings = settings
        self._client = klaviyo_client or KlaviyoClient(settings)

    def get_performance_for_campaign(self, campaign_code: str) -> KlaviyoPerformanceMetrics | None:
        """Return historical performance metrics for a campaign code, or None if unavailable."""
        try:
            return self._client.get_campaign_performance(campaign_code)
        except KlaviyoClientError as exc:
            logger.warning(
                "Klaviyo performance lookup failed for {}: {}",
                campaign_code,
                exc,
            )
            return None
