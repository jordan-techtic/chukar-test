"""Loguru logging configuration."""

import sys

from loguru import logger


def setup_logging() -> None:
    """Configure application logging with stderr and rotating file output."""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="10 days",
        level="INFO",
        encoding="utf-8",
    )


__all__ = ["logger", "setup_logging"]
