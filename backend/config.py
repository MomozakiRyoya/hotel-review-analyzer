"""
Configuration management for the Hotel Review Analyzer application.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = "Hotel Review Analyzer"
    app_version: str = "1.0.0"
    debug: bool = True

    # Server Settings
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    streamlit_port: int = 8501

    # OTA API Credentials
    rakuten_app_id: Optional[str] = None
    jalan_api_key: Optional[str] = None
    booking_api_url: str = "https://distribution-xml.booking.com/2.7/json/reviews"
    booking_username: Optional[str] = None
    booking_password: Optional[str] = None

    # Rate Limiting
    request_delay_seconds: float = 1.0
    max_retries: int = 3
    retry_backoff_factor: float = 2.0

    # Data Directories
    data_dir: Path = Path("./data")
    cache_dir: Path = Path("./data/cache")
    temp_dir: Path = Path("./data/temp")
    output_dir: Path = Path("./output")

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
        for directory in [self.data_dir, self.cache_dir, self.temp_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
