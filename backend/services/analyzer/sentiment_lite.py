"""
Lightweight sentiment analysis for Vercel deployment.
Uses keyword-based approach instead of heavy ML models.
"""
from typing import List
from loguru import logger

from backend.models.review import Review


class SentimentAnalyzerLite:
    """Lightweight sentiment analyzer using keyword matching."""

    def __init__(self):
        """Initialize with keyword dictionaries."""
        # Positive keywords
        self.positive_keywords = {
            '良い', '良かった', '最高', '素晴らしい', '快適', '綺麗', '清潔',
            '親切', '丁寧', '満足', 'おすすめ', 'オススメ', '便利', '美味しい',
            'きれい', 'キレイ', '良好', '快適', '心地よい', 'おもてなし',
            '感動', '完璧', '素敵', 'すてき', '広い', '新しい', '清潔感',
            'コスパ', 'お得', '安い', '静か', '落ち着く', '癒', 'リラックス'
        }

        # Negative keywords
        self.negative_keywords = {
            '悪い', '悪かった', '最悪', 'ダメ', 'だめ', '汚い', '不便', '不満',
            '残念', 'がっかり', 'ガッカリ', '期待外れ', '古い', '狭い', 'うるさい',
            '高い', '不親切', '不潔', '臭い', 'におい', 'ニオイ', '壊れ', '故障',
            '対応が悪', '最低', 'ひどい', '酷い', '失望', '二度と', 'もう来ない',
            '不快', '不衛生', 'カビ', 'ゴキブリ', '虫', 'ボロボロ', 'ぼろぼろ'
        }

    def analyze_reviews(self, reviews: List[Review]) -> List[Review]:
        """
        Analyze sentiment for a list of reviews.

        Args:
            reviews: List of Review objects

        Returns:
            Reviews with sentiment fields populated
        """
        logger.info(f"Analyzing sentiment for {len(reviews)} reviews (lightweight)")

        for review in reviews:
            if not review.comment:
                continue

            # Count positive and negative keywords
            positive_count = sum(1 for kw in self.positive_keywords if kw in review.comment)
            negative_count = sum(1 for kw in self.negative_keywords if kw in review.comment)

            # Calculate sentiment score (-1 to 1)
            total = positive_count + negative_count
            if total == 0:
                sentiment_score = 0.0
                sentiment = "neutral"
            else:
                sentiment_score = (positive_count - negative_count) / (total * 2)

                if sentiment_score > 0.2:
                    sentiment = "positive"
                elif sentiment_score < -0.2:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"

            review.sentiment = sentiment
            review.sentiment_score = round(sentiment_score, 3)
            review.sentiment_confidence = min(0.7 + (total * 0.05), 0.95)  # Confidence based on keyword count

        logger.info(f"✅ Sentiment analysis complete")
        return reviews

    def get_sentiment_distribution(self, reviews: List[Review]) -> dict:
        """Get distribution of sentiments."""
        distribution = {"positive": 0, "neutral": 0, "negative": 0}

        for review in reviews:
            if review.sentiment:
                distribution[review.sentiment] += 1

        return distribution

    def get_average_sentiment(self, reviews: List[Review]) -> float:
        """Calculate average sentiment score."""
        scores = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
        return round(sum(scores) / len(scores), 3) if scores else 0.0
