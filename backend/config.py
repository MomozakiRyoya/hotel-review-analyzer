"""
Configuration management for the Hotel Review Analyzer application.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = "Hotel Review Analyzer"
    app_version: str = "1.0.0"
    debug: bool = True
    use_demo_reviews: bool = True  # Enable demo reviews when scraping fails

    @field_validator('debug', 'use_demo_reviews', mode='before')
    @classmethod
    def parse_bool(cls, v):
        """Parse boolean values from environment variables."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() in ('true', '1', 'yes', 'on')
        return bool(v)

    # Server Settings
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    streamlit_port: int = 8501

    # OTA API Credentials (for reference only - actual keys are in backend/services/ota/api_keys.py)
    booking_api_url: str = "https://distribution-xml.booking.com/2.7/json/reviews"
    booking_username: Optional[str] = None
    booking_password: Optional[str] = None

    # Rate Limiting
    request_delay_seconds: float = 1.0
    max_retries: int = 3
    retry_backoff_factor: float = 2.0

    # Data Directories (use /tmp for serverless environments like Vercel)
    data_dir: Path = Path("/tmp/data") if os.getenv("VERCEL") else Path("./data")
    cache_dir: Path = Path("/tmp/data/cache") if os.getenv("VERCEL") else Path("./data/cache")
    temp_dir: Path = Path("/tmp/data/temp") if os.getenv("VERCEL") else Path("./data/temp")
    output_dir: Path = Path("/tmp/output") if os.getenv("VERCEL") else Path("./output")

    # NLP Model Settings
    sentiment_model: str = "daigo/bert-base-japanese-sentiment"
    batch_size: int = 32
    max_length: int = 512

    # Logging
    log_level: str = "INFO"
    log_file: Path = Path("./data/app.log")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        try:
            for directory in [self.data_dir, self.cache_dir, self.temp_dir, self.output_dir]:
                directory.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # In serverless environments, directory creation may fail
            # This is acceptable as /tmp directories may be pre-created or created on-demand
            pass


# Global settings instance
settings = Settings()
# Don't call ensure_directories() at module level for serverless compatibility
# It will be called during app startup event instead
