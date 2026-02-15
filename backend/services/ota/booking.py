"""
Booking.com OTA client (API).
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
import random

from backend.models.review import Review, OTASource
from backend.services.ota.base import OTAClient
from backend.services.ota.api_keys import get_booking_credentials
from backend.utils.exceptions import HotelNotFoundError, ReviewFetchError, AuthenticationError


class BookingClient(OTAClient):
    """Booking.com client using Guest Review API."""

    BASE_URL = "https://distribution-xml.booking.com/2.7/json"

    def __init__(self):
        """Initialize Booking.com client."""
        super().__init__()
        self.config = get_booking_credentials()
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.api_url = self.config.get("url")
        self.enabled = self.config.get("enabled", False)

        if not self.enabled:
            logger.warning("Booking.com API not enabled - using demo data")

    def _get_source(self) -> OTASource:
        """Get OTA source identifier."""
        return OTASource.BOOKING

    async def search_hotels(
        self,
        hotel_name: str,
        location: Optional[str] = None
    ) -> List[dict]:
        """
        Search for hotels on Booking.com.

        Note: This is a mock implementation for Phase 2.
        Real implementation would use Booking.com API.

        Args:
            hotel_name: Hotel name to search
            location: Optional location filter

        Returns:
            List of hotel search results

        Raises:
            HotelNotFoundError: If no hotels found
            AuthenticationError: If API credentials invalid
        """
        logger.info(f"Searching Booking.com for hotel: {hotel_name}")

        if not self.enabled:
            logger.info("Using demo data - Booking.com API not enabled")
            return self._mock_search_hotels(hotel_name)

        # TODO: Implement real Booking.com API call
        return self._mock_search_hotels(hotel_name)

    def _mock_search_hotels(self, hotel_name: str) -> List[dict]:
        """Mock hotel search for demo."""
        return [{
            "id": "booking_hotel_001",
            "name": hotel_name,
            "url": "https://www.booking.com/hotel/jp/sample.html",
            "rating": 8.5,  # Booking uses 10-point scale
            "review_count": 180
        }]

    async def fetch_reviews(
        self,
        hotel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        languages: Optional[List[str]] = None
    ) -> List[Review]:
        """
        Fetch reviews from Booking.com.

        Note: This is a mock implementation for Phase 2.
        Real implementation would use Booking.com Guest Review API.

        Args:
            hotel_id: Booking.com hotel ID
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum reviews to fetch

        Returns:
            List of Review objects

        Raises:
            ReviewFetchError: If fetching fails
            AuthenticationError: If API credentials invalid
        """
        logger.info(f"Fetching Booking.com reviews for hotel: {hotel_id}")

        if languages is None:
            languages = ['en', 'ja']

        if not self.enabled:
            logger.info("Using demo data - Booking.com API not enabled")
            reviews = self._generate_mock_reviews(hotel_id, limit, languages)
        else:
            # TODO: Implement real Booking.com API call
            reviews = self._generate_mock_reviews(hotel_id, limit, languages)

        # Filter by date
        reviews = self._filter_reviews_by_date(reviews, start_date, end_date)

        # Apply limit
        reviews = self._limit_reviews(reviews, limit)

        logger.info(f"Fetched {len(reviews)} reviews from Booking.com")
        return reviews

    def normalize_review(
        self,
        raw_data: dict,
        hotel_id: str,
        hotel_name: str
    ) -> Review:
        """
        Normalize Booking.com review data to Review model.

        Note: Booking.com uses 10-point scale, converted to 5-point.

        Args:
            raw_data: Raw review data from Booking.com
            hotel_id: Hotel ID
            hotel_name: Hotel name

        Returns:
            Normalized Review object
        """
        # Convert Booking.com's 10-point scale to 5-point scale
        original_rating = float(raw_data.get("rating", 0))
        normalized_rating = original_rating / 2.0

        return Review(
            review_id=raw_data.get("id", ""),
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            source=self.source,
            title=raw_data.get("title"),
            comment=raw_data.get("comment", ""),
            rating=normalized_rating,
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

    def _generate_mock_reviews(self, hotel_id: str, count: int, languages: List[str]) -> List[Review]:
        """
        Generate mock reviews for testing.

        Args:
            hotel_id: Hotel ID
            count: Number of reviews to generate
            languages: List of language codes (ja, en, ko, zh)

        Returns:
            List of mock Review objects
        """
        # Multi-language review templates
        review_templates = {
            'en': [
                "Excellent hotel with great service. The staff was very helpful and friendly.",
                "Clean rooms and good location. Would definitely stay again.",
                "The breakfast was amazing. Room was spacious and comfortable.",
                "Good value for money. Location is perfect for sightseeing.",
                "Room was a bit small but overall good experience."
            ],
            'ja': [
                "素晴らしいホテルでした。スタッフの対応が非常に親切で丁寧でした。",
                "清潔な部屋と良い立地。また泊まりたいです。",
                "朝食が美味しかったです。部屋は広くて快適でした。",
                "コストパフォーマンスが良い。観光に最適な立地です。",
                "部屋は少し小さめでしたが、全体的に良い体験でした。"
            ],
            'ko': [
                "훌륭한 호텔이었습니다. 직원들이 매우 친절하고 도움이 되었습니다.",
                "깨끗한 객실과 좋은 위치. 다시 묵고 싶습니다.",
                "조식이 훌륭했습니다. 객실은 넓고 편안했습니다.",
                "가성비가 좋습니다. 관광하기에 완벽한 위치입니다.",
                "객실이 조금 작았지만 전반적으로 좋은 경험이었습니다."
            ],
            'zh': [
                "优秀的酒店，服务很好。工作人员非常乐于助人且友好。",
                "房间干净，位置好。一定会再来住宿。",
                "早餐很棒。房间宽敞舒适。",
                "性价比高。观光的理想位置。",
                "房间有点小，但总体体验不错。"
            ]
        }

        reviews = []
        base_date = datetime.utcnow()

        # Distribute reviews across selected languages
        reviews_per_language = count // len(languages) if languages else count

        for lang in languages:
            templates = review_templates.get(lang, review_templates['en'])
            lang_count = min(reviews_per_language, len(templates))

            for i in range(lang_count):
                # Booking.com uses 10-point scale
                rating_10_scale = random.choice([7, 7.5, 8, 8, 8.5, 9, 9, 9.5, 10])
                review_date = base_date - timedelta(days=random.randint(1, 365))

                raw_data = {
                    "id": f"booking_rev_{hotel_id}_{lang}_{i}",
                    "title": "Great stay" if i % 2 == 0 else None,
                    "comment": templates[i % len(templates)],
                    "rating": rating_10_scale,
                    "rating_details": {
                        "cleanliness": random.uniform(7, 10),
                        "comfort": random.uniform(7, 10),
                        "location": random.uniform(7, 10),
                        "facilities": random.uniform(7, 10),
                        "staff": random.uniform(8, 10),
                        "value_for_money": random.uniform(7, 10)
                    },
                    "reviewer_name": f"Guest_{lang}_{i}",
                    "age_group": random.choice(["25-34", "35-44", "45-54", "55+"]),
                    "gender": random.choice(["Male", "Female", None]),
                    "stay_date": review_date - timedelta(days=random.randint(5, 20)),
                    "review_date": review_date,
                    "trip_type": random.choice(["Leisure", "Business", "Family", "Couple"]),
                    "room_type": random.choice(["Standard Room", "Deluxe Room", "Suite"]),
                    "helpful_count": random.randint(0, 20),
                    "url": f"https://www.booking.com/hotel/jp/{hotel_id}.html",
                    "language": lang
                }

                review = self.normalize_review(raw_data, hotel_id, f"Sample Hotel {hotel_id}")
                reviews.append(review)

        return reviews
