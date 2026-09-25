"""Rate limiting configuration using slowapi."""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address


def _is_rate_limit_enabled() -> bool:
    """Return True unless rate limiting is explicitly disabled via env."""
    value = os.environ.get("RATE_LIMIT_ENABLED", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


limiter = Limiter(
    key_func=get_remote_address,
    enabled=_is_rate_limit_enabled(),
)
