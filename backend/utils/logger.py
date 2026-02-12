"""
Logging configuration using loguru.
"""
import sys
from loguru import logger
from pathlib import Path
from backend.config import settings


def setup_logger() -> None:
    """Configure loguru logger with file and console handlers."""

    # Remove default handler
    logger.remove()

    # Console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    # File handler
    if settings.log_file:
        settings.log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            settings.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
        )

    logger.info(f"Logger initialized: level={settings.log_level}")


# Initialize logger on module import
setup_logger()
