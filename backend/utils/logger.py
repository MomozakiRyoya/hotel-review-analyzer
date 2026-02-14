"""
Logging configuration using loguru.
"""
import sys
import os
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

    # File handler (skip in serverless environments like Vercel)
    if settings.log_file and not os.getenv("VERCEL"):
        try:
            settings.log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                settings.log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level=settings.log_level,
                rotation="10 MB",
                retention="1 week",
                compression="zip",
            )
        except (OSError, PermissionError):
            # In serverless environments, file logging may not be available
            pass

    logger.info(f"Logger initialized: level={settings.log_level}")


# Don't initialize logger at module level for serverless compatibility
# It will be called explicitly from main.py
