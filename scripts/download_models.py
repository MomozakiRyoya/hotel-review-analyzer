#!/usr/bin/env python3
"""
Download NLP models for sentiment analysis.
This script downloads the required BERT model for Japanese sentiment analysis.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from backend.config import settings
from loguru import logger


def download_sentiment_model():
    """Download BERT model for sentiment analysis."""
    logger.info(f"Downloading sentiment analysis model: {settings.sentiment_model}")

    try:
        # Download tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(settings.sentiment_model)
        logger.info("✅ Tokenizer downloaded successfully")

        # Download model
        logger.info("Downloading model...")
        model = AutoModelForSequenceClassification.from_pretrained(
            settings.sentiment_model
        )
        logger.info("✅ Model downloaded successfully")

        # Save to cache
        cache_dir = settings.cache_dir / "transformers"
        cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving model to cache: {cache_dir}")
        tokenizer.save_pretrained(cache_dir / "tokenizer")
        model.save_pretrained(cache_dir / "model")

        logger.info("✅ Model saved to cache")
        logger.info("🎉 All models downloaded successfully!")

        return True

    except Exception as e:
        logger.error(f"❌ Error downloading models: {str(e)}")
        return False


def main():
    """Main function."""
    logger.info("🏨 Hotel Review Analyzer - NLP Model Download")
    logger.info("=" * 50)

    success = download_sentiment_model()

    if success:
        logger.info("\n✅ Setup complete! You can now run the application.")
        return 0
    else:
        logger.error("\n❌ Setup failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
