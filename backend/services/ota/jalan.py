"""
Jalan.net OTA client (web scraping).
"""
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from loguru import logger

from backend.models.review import Review, OTASource
from backend.services.ota.base import OTAClient
from backend.utils.exceptions import HotelNotFoundError, ReviewFetchError


class JalanClient(OTAClient):
    """Jalan.net client using web scraping."""

    BASE_URL = "https://www.jalan.net"

    def _get_source(self) -> OTASource:
        """Get OTA source identifier."""
        return OTASource.JALAN

    async def search_hotels(
        self,
        hotel_name: str,
        location: Optional[str] = None
    ) -> List[dict]:
        """
        Search for hotels on Jalan.

        Note: This is a mock implementation for Phase 2.
        Real implementation would scrape Jalan search results.

        Args:
            hotel_name: Hotel name to search
            location: Optional location filter

        Returns:
            List of hotel search results

        Raises:
            HotelNotFoundError: If no hotels found
        """
        logger.info(f"Searching Jalan for hotel: {hotel_name}")

        # Mock implementation - returns sample data
        # In production, this would scrape jalan.net search results
        mock_results = [
            {
                "id": "jalan_hotel_001",
                "name": hotel_name,
                "url": f"{self.BASE_URL}/yad000000/",
                "rating": 4.2,
                "review_count": 150
            }
        ]

        if not mock_results:
            raise HotelNotFoundError(f"No hotels found for: {hotel_name}")

        logger.info(f"Found {len(mock_results)} hotels on Jalan")
        return mock_results

    async def fetch_reviews(
        self,
        hotel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Review]:
        """
        Fetch reviews from Jalan.

        Note: This is a mock implementation for Phase 2.
        Real implementation would scrape Jalan review pages.

        Args:
            hotel_id: Jalan hotel ID
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum reviews to fetch

        Returns:
            List of Review objects

        Raises:
            ReviewFetchError: If fetching fails
        """
        logger.info(f"Fetching Jalan reviews for hotel: {hotel_id}")

        try:
            # Mock implementation - generates sample reviews
            # In production, this would scrape actual review pages
            reviews = self._generate_mock_reviews(hotel_id, limit)

            # Filter by date
            reviews = self._filter_reviews_by_date(reviews, start_date, end_date)

            # Apply limit
            reviews = self._limit_reviews(reviews, limit)

            logger.info(f"Fetched {len(reviews)} reviews from Jalan")
            return reviews

        except Exception as e:
            logger.error(f"Failed to fetch Jalan reviews: {str(e)}")
            raise ReviewFetchError(f"Jalan review fetch failed: {str(e)}")

    def normalize_review(
        self,
        raw_data: dict,
        hotel_id: str,
        hotel_name: str
    ) -> Review:
        """
        Normalize Jalan review data to Review model.

        Args:
            raw_data: Raw review data from Jalan
            hotel_id: Hotel ID
            hotel_name: Hotel name

        Returns:
            Normalized Review object
        """
        return Review(
            review_id=raw_data.get("id", ""),
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            source=self.source,
            title=raw_data.get("title"),
            comment=raw_data.get("comment", ""),
            rating=float(raw_data.get("rating", 0)),
            rating_details=raw_data.get("rating_details"),
            reviewer_name=raw_data.get("reviewer_name"),
            reviewer_age_group=raw_data.get("age_group"),
            reviewer_gender=raw_data.get("gender"),
            stay_date=raw_data.get("stay_date"),
            review_date=raw_data.get("review_date", datetime.utcnow()),
            trip_type=raw_data.get("trip_type"),
            room_type=raw_data.get("room_type"),
            helpful_count=raw_data.get("helpful_count", 0),
            url=raw_data.get("url"),
            raw_data=raw_data
        )

    def _generate_mock_reviews(self, hotel_id: str, count: int) -> List[Review]:
        """
        Generate mock reviews for testing.

        This will be replaced with actual scraping logic.

        Args:
            hotel_id: Hotel ID
            count: Number of reviews to generate

        Returns:
            List of mock Review objects
        """
        import random
        from datetime import timedelta

        mock_comments = [
            "部屋がとても綺麗で快適でした。スタッフの対応も素晴らしかったです。",
            "立地が良く、観光に便利でした。朝食も美味しかったです。",
            "少し古い建物ですが、清潔に保たれていました。",
            "部屋が狭く、設備が古いです。改善が必要だと思います。",
            "コストパフォーマンスが良いホテルです。また利用したいです。",
            "温泉が素晴らしく、とてもリラックスできました。",
            "接客が丁寧で、気持ちよく滞在できました。",
            "清潔感があり、安心して泊まれました。",
            "Wi-Fiの速度が遅く、不便でした。",
            "景色が綺麗で、癒されました。"
        ]

        reviews = []
        base_date = datetime.utcnow()

        for i in range(min(count, 10)):  # Limit mock data to 10
            rating = random.choice([3, 4, 4, 5, 5, 5])  # Bias towards positive
            review_date = base_date - timedelta(days=random.randint(1, 365))

            raw_data = {
                "id": f"jalan_rev_{hotel_id}_{i}",
                "title": "宿泊の感想" if i % 2 == 0 else None,
                "comment": random.choice(mock_comments),
                "rating": rating,
                "rating_details": {
                    "service": random.randint(3, 5),
                    "location": random.randint(3, 5),
                    "room": random.randint(3, 5),
                    "bath": random.randint(3, 5),
                    "meal": random.randint(3, 5)
                },
                "reviewer_name": f"ゲスト{i}",
                "age_group": random.choice(["20代", "30代", "40代", "50代"]),
                "gender": random.choice(["男性", "女性"]),
                "stay_date": review_date - timedelta(days=7),
                "review_date": review_date,
                "trip_type": random.choice(["レジャー", "ビジネス", "家族旅行"]),
                "room_type": "スタンダードルーム",
                "helpful_count": random.randint(0, 10),
                "url": f"{self.BASE_URL}/yad{hotel_id}/kuchikomi/"
            }

            review = self.normalize_review(raw_data, hotel_id, f"サンプルホテル {hotel_id}")
            reviews.append(review)

        return reviews
