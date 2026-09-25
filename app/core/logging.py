"""Loguru logging configuration."""

import sys

from loguru import logger


def setup_logging(environment: str = "development") -> None:
    """Configure loguru sinks for stderr and rotating file output."""
    logger.remove()
    log_level = "DEBUG" if environment == "development" else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="10 days",
        level=log_level,
        enqueue=True,
    )


__all__ = ["logger", "setup_logging"]
