"""
Sentiment analysis service using BERT.
"""
from typing import List, Tuple, Dict, Literal
from loguru import logger
import time

from backend.models.review import Review
from backend.config import settings
from backend.utils.exceptions import SentimentAnalysisError


class SentimentAnalyzer:
    """
    Sentiment analyzer using Japanese BERT model.

    Note: This is a mock implementation for Phase 3.
    Real implementation would use transformers library with BERT model.
    """

    def __init__(self):
        """Initialize sentiment analyzer."""
        self.model_name = settings.sentiment_model
        self.batch_size = settings.batch_size
        self.model = None
        self.tokenizer = None
        logger.info(f"Sentiment analyzer initialized (model: {self.model_name})")

    def _load_model(self):
        """
        Load BERT model and tokenizer.

        Note: Mock implementation. Real implementation would load actual model:

        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        )
        """
        logger.info("Loading sentiment analysis model...")
        # Mock: Model already loaded
        logger.info("✅ Model loaded successfully")

    def analyze_batch(
        self,
        texts: List[str]
    ) -> List[Tuple[str, float, float]]:
        """
        Analyze sentiment for a batch of texts.

        Args:
            texts: List of text strings to analyze

        Returns:
            List of (sentiment, score, confidence) tuples

        Raises:
            SentimentAnalysisError: If analysis fails
        """
        if not texts:
            return []

        try:
            # Mock implementation using simple heuristics
            results = []

            for text in texts:
                sentiment, score, confidence = self._analyze_text_mock(text)
                results.append((sentiment, score, confidence))

            return results

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            raise SentimentAnalysisError(f"Sentiment analysis failed: {str(e)}")

    def _analyze_text_mock(
        self,
        text: str
    ) -> Tuple[Literal["positive", "negative", "neutral"], float, float]:
        """
        Mock sentiment analysis using keyword matching.

        Real implementation would use BERT model inference.

        Args:
            text: Text to analyze

        Returns:
            (sentiment, score, confidence) tuple
        """
        # Positive keywords
        positive_keywords = [
            "素晴らしい", "良い", "最高", "綺麗", "快適", "満足", "おすすめ",
            "丁寧", "美味しい", "清潔", "親切", "便利", "広い", "豪華",
            "excellent", "great", "good", "amazing", "perfect", "clean",
            "comfortable", "beautiful", "helpful", "friendly"
        ]

        # Negative keywords
        negative_keywords = [
            "悪い", "最悪", "汚い", "不満", "狭い", "古い", "遅い", "うるさい",
            "高い", "不便", "残念", "改善", "問題", "不快",
            "bad", "terrible", "poor", "dirty", "small", "old", "noisy",
            "expensive", "disappointing", "problem"
        ]

        # Count matches
        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)

        # Calculate score (-1 to 1)
        total_count = positive_count + negative_count
        if total_count == 0:
            sentiment = "neutral"
            score = 0.0
            confidence = 0.5
        elif positive_count > negative_count:
            sentiment = "positive"
            score = min(positive_count / (total_count + 1), 1.0)
            confidence = min(0.6 + (positive_count - negative_count) * 0.1, 0.95)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -min(negative_count / (total_count + 1), 1.0)
            confidence = min(0.6 + (negative_count - positive_count) * 0.1, 0.95)
        else:
            sentiment = "neutral"
            score = 0.0
            confidence = 0.6

        return sentiment, round(score, 3), round(confidence, 3)

    def analyze_reviews(
        self,
        reviews: List[Review]
    ) -> List[Review]:
        """
        Analyze sentiment for list of reviews.

        Args:
            reviews: List of Review objects

        Returns:
            List of Review objects with sentiment fields populated
        """
        if not reviews:
            return reviews

        logger.info(f"Analyzing sentiment for {len(reviews)} reviews")
        start_time = time.time()

        try:
            # Extract text from reviews
            texts = [review.comment for review in reviews]

            # Analyze in batches
            all_results = []
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                batch_results = self.analyze_batch(batch_texts)
                all_results.extend(batch_results)

                logger.debug(
                    f"Processed batch {i // self.batch_size + 1} "
                    f"({len(batch_results)} reviews)"
                )

            # Update reviews with sentiment results
            for review, (sentiment, score, confidence) in zip(reviews, all_results):
                review.sentiment = sentiment
                review.sentiment_score = score
                review.confidence = confidence

            elapsed = time.time() - start_time
            logger.info(
                f"✅ Sentiment analysis complete: {len(reviews)} reviews "
                f"in {elapsed:.2f}s ({len(reviews)/elapsed:.1f} reviews/s)"
            )

            return reviews

        except Exception as e:
            logger.error(f"Failed to analyze reviews: {str(e)}")
            raise SentimentAnalysisError(f"Failed to analyze reviews: {str(e)}")

    def get_sentiment_distribution(
        self,
        reviews: List[Review]
    ) -> Dict[str, int]:
        """
        Get sentiment distribution from reviews.

        Args:
            reviews: List of analyzed reviews

        Returns:
            Dictionary with sentiment counts
        """
        distribution = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        for review in reviews:
            if review.sentiment:
                distribution[review.sentiment] += 1

        return distribution

    def get_average_sentiment(
        self,
        reviews: List[Review]
    ) -> float:
        """
        Calculate average sentiment score.

        Args:
            reviews: List of analyzed reviews

        Returns:
            Average sentiment score (-1 to 1)
        """
        scores = [r.sentiment_score for r in reviews if r.sentiment_score is not None]

        if not scores:
            return 0.0

        return round(sum(scores) / len(scores), 3)
