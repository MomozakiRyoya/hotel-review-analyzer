"""
Keyword extraction service using Janome.
"""
from typing import List, Dict, Set, Optional
from collections import Counter
import re
from loguru import logger

from backend.models.review import Review
from backend.models.analysis_result import KeywordResult
from backend.utils.exceptions import KeywordExtractionError


class KeywordExtractor:
    """
    Keyword extractor using Janome morphological analyzer.

    Note: This is a mock implementation for Phase 3.
    Real implementation would use Janome library.
    """

    # Japanese stopwords
    STOPWORDS: Set[str] = {
        "ホテル", "宿", "部屋", "料理", "食事", "朝食", "夕食", "風呂", "温泉",
        "スタッフ", "フロント", "サービス", "施設", "宿泊", "利用", "予約",
        "こと", "もの", "ため", "よう", "そう", "とても", "すごく", "かなり",
        "ちょっと", "少し", "とき", "ところ", "場合", "方", "人", "お客様",
        "hotel", "room", "staff", "service", "stay", "food", "breakfast"
    }

    def __init__(self):
        """Initialize keyword extractor."""
        self.tokenizer = None
        logger.info("Keyword extractor initialized")

    def _load_tokenizer(self):
        """
        Load Janome tokenizer.

        Note: Mock implementation. Real implementation would load Janome:

        from janome.tokenizer import Tokenizer
        self.tokenizer = Tokenizer()
        """
        logger.info("Loading Janome tokenizer...")
        # Mock: Tokenizer already loaded
        logger.info("✅ Tokenizer loaded successfully")

    def extract_keywords_from_reviews(
        self,
        reviews: List[Review],
        top_n: int = 30,
        min_frequency: int = 2
    ) -> List[KeywordResult]:
        """
        Extract keywords from list of reviews.

        Args:
            reviews: List of reviews
            top_n: Number of top keywords to return
            min_frequency: Minimum frequency threshold

        Returns:
            List of KeywordResult objects

        Raises:
            KeywordExtractionError: If extraction fails
        """
        if not reviews:
            return []

        logger.info(f"Extracting keywords from {len(reviews)} reviews")

        try:
            # Extract all keywords
            all_keywords = []

            for review in reviews:
                keywords = self._extract_from_text(review.comment)
                all_keywords.extend(keywords)

            # Count frequencies
            keyword_freq = Counter(all_keywords)

            # Filter by minimum frequency
            filtered_keywords = {
                kw: freq for kw, freq in keyword_freq.items()
                if freq >= min_frequency and kw not in self.STOPWORDS
            }

            # Calculate TF-IDF-like scores
            max_freq = max(filtered_keywords.values()) if filtered_keywords else 1
            keyword_scores = {}

            for keyword, freq in filtered_keywords.items():
                # Simple scoring: normalized frequency
                score = freq / max_freq
                keyword_scores[keyword] = (freq, score)

            # Sort by score and take top N
            sorted_keywords = sorted(
                keyword_scores.items(),
                key=lambda x: (x[1][1], x[1][0]),
                reverse=True
            )[:top_n]

            # Create KeywordResult objects
            results = []
            for keyword, (freq, score) in sorted_keywords:
                category = self._categorize_keyword(keyword, reviews)
                results.append(
                    KeywordResult(
                        keyword=keyword,
                        frequency=freq,
                        score=round(score, 3),
                        category=category
                    )
                )

            logger.info(f"✅ Extracted {len(results)} keywords")
            return results

        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            raise KeywordExtractionError(f"Keyword extraction failed: {str(e)}")

    def _extract_from_text(self, text: str) -> List[str]:
        """
        Extract keywords from text using morphological analysis.

        Note: Mock implementation. Real implementation would use Janome.

        Args:
            text: Text to analyze

        Returns:
            List of keywords
        """
        # Mock implementation using simple regex
        # Real implementation would use: self.tokenizer.tokenize(text)

        # Remove punctuation and split
        text = re.sub(r'[。、！？\.,!?]', ' ', text)
        words = text.split()

        # Filter: only keep words with 2+ characters
        keywords = []
        for word in words:
            # Remove common particles (は、が、を、に、で、と、も、から、まで)
            word = re.sub(r'[はがをにでともからまで]$', '', word)

            if len(word) >= 2 and word not in self.STOPWORDS:
                keywords.append(word)

        return keywords

    def _categorize_keyword(
        self,
        keyword: str,
        reviews: List[Review]
    ) -> Optional[str]:
        """
        Categorize keyword as positive/negative/neutral.

        Args:
            keyword: Keyword to categorize
            reviews: Reviews for context

        Returns:
            Category string or None
        """
        # Simple categorization based on sentiment of reviews containing keyword
        positive_words = {
            "良い", "素晴らしい", "綺麗", "快適", "満足", "最高", "美味しい",
            "清潔", "親切", "丁寧", "便利", "広い", "新しい",
            "good", "great", "excellent", "clean", "comfortable", "nice",
            "beautiful", "friendly", "helpful"
        }

        negative_words = {
            "悪い", "汚い", "狭い", "古い", "不満", "残念", "うるさい",
            "高い", "不便", "遅い", "問題",
            "bad", "poor", "dirty", "small", "old", "noisy", "expensive",
            "disappointing"
        }

        if keyword in positive_words:
            return "positive"
        elif keyword in negative_words:
            return "negative"
        else:
            return "neutral"

    def extract_by_sentiment(
        self,
        reviews: List[Review],
        sentiment: str,
        top_n: int = 10
    ) -> List[KeywordResult]:
        """
        Extract keywords from reviews with specific sentiment.

        Args:
            reviews: List of reviews
            sentiment: Sentiment filter (positive/negative/neutral)
            top_n: Number of top keywords

        Returns:
            List of KeywordResult objects
        """
        # Filter reviews by sentiment
        filtered_reviews = [
            r for r in reviews
            if r.sentiment == sentiment
        ]

        if not filtered_reviews:
            return []

        # Extract keywords
        keywords = self.extract_keywords_from_reviews(
            filtered_reviews,
            top_n=top_n,
            min_frequency=1
        )

        # Force category to match sentiment
        for kw in keywords:
            kw.category = sentiment

        return keywords

    def get_keyword_trends(
        self,
        reviews: List[Review],
        keyword: str
    ) -> Dict:
        """
        Get trend data for a specific keyword.

        Args:
            reviews: List of reviews
            keyword: Keyword to track

        Returns:
            Dictionary with trend data
        """
        # Count occurrences over time
        mentions_by_month = {}

        for review in reviews:
            if keyword in review.comment:
                month_key = review.review_date.strftime("%Y-%m")
                mentions_by_month[month_key] = mentions_by_month.get(month_key, 0) + 1

        return {
            "keyword": keyword,
            "total_mentions": sum(mentions_by_month.values()),
            "mentions_by_month": mentions_by_month
        }
