"""
Expedia OTA client.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
import random

from backend.models.review import Review, OTASource
from backend.services.ota.base import OTAClient
from backend.services.ota.api_keys import get_expedia_credentials
from backend.utils.exceptions import HotelNotFoundError, ReviewFetchError, AuthenticationError


class ExpediaClient(OTAClient):
    """Expedia client for hotel reviews."""

    def __init__(self):
        """Initialize Expedia client."""
        super().__init__()
        self.config = get_expedia_credentials()
        self.api_key = self.config.get("api_key")
        self.api_secret = self.config.get("api_secret")
        self.endpoint = self.config.get("endpoint")
        self.enabled = self.config.get("enabled", False)

        if not self.enabled:
            logger.warning("Expedia API not enabled - using demo data")

    def _get_source(self) -> OTASource:
        """Get OTA source identifier."""
        return OTASource.EXPEDIA

    async def search_hotels(
        self,
        hotel_name: str,
        location: Optional[str] = None
    ) -> List[dict]:
        """
        Search for hotels on Expedia.

        Args:
            hotel_name: Hotel name to search
            location: Optional location filter

        Returns:
            List of hotel search results
        """
        logger.info(f"Searching Expedia for hotel: {hotel_name}")

        if not self.enabled:
            logger.info("Using demo data - Expedia API not enabled")
            return self._mock_search_hotels(hotel_name)

        # TODO: Implement real Expedia API call
        return self._mock_search_hotels(hotel_name)

    async def fetch_reviews(
        self,
        hotel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        languages: Optional[List[str]] = None
    ) -> List[Review]:
        """
        Fetch reviews from Expedia.

        Args:
            hotel_id: Expedia hotel ID
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum reviews to fetch

        Returns:
            List of Review objects
        """
        logger.info(f"Fetching Expedia reviews for hotel: {hotel_id}")

        if languages is None:
            languages = ['en', 'ja']

        if not self.enabled:
            logger.info("Using demo data - Expedia API not enabled")
            reviews = self._generate_demo_reviews(hotel_id, limit, languages)
        else:
            # TODO: Implement real Expedia API call
            reviews = self._generate_demo_reviews(hotel_id, limit, languages)

        # Filter by date
        reviews = self._filter_reviews_by_date(reviews, start_date, end_date)

        # Apply limit
        reviews = self._limit_reviews(reviews, limit)

        logger.info(f"Fetched {len(reviews)} reviews from Expedia")
        return reviews

    def normalize_review(
        self,
        raw_data: dict,
        hotel_id: str,
        hotel_name: str
    ) -> Review:
        """
        Normalize Expedia review data to Review model.

        Args:
            raw_data: Raw review data
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

    def _mock_search_hotels(self, hotel_name: str) -> List[dict]:
        """Mock hotel search for demo."""
        return [{
            "id": "expedia_hotel_001",
            "name": hotel_name,
            "url": "https://www.expedia.com/hotel/sample",
            "rating": 4.3,
            "review_count": 250
        }]

    def _generate_demo_reviews(self, hotel_id: str, count: int, languages: List[str]) -> List[Review]:
        """Generate realistic demo reviews for Expedia."""
        reviews = []
        base_date = datetime.utcnow()

        # Multi-language review templates
        review_templates = {
            'en': [
                {"title": "Excellent stay!", "comment": "Great location near the station. Clean rooms and friendly staff.", "rating": 4.5},
                {"title": "Good value", "comment": "The hotel offers great value. Rooms are well-maintained.", "rating": 4.0},
                {"title": "Perfect for business", "comment": "Convenient location. Fast WiFi and comfortable work desk.", "rating": 4.5}
            ],
            'ja': [
                {"title": "最高の滞在！", "comment": "駅に近い素晴らしい立地。部屋は清潔でスタッフも親切でした。", "rating": 4.5},
                {"title": "お値打ち", "comment": "ホテルは素晴らしいコスパを提供しています。部屋は良く維持されています。", "rating": 4.0},
                {"title": "ビジネスに最適", "comment": "便利な立地。高速WiFiと快適なワークデスク。", "rating": 4.5}
            ],
            'ko': [
                {"title": "훌륭한 숙박!", "comment": "역 근처의 좋은 위치. 깨끗한 객실과 친절한 직원.", "rating": 4.5},
                {"title": "좋은 가치", "comment": "호텔은 훌륭한 가치를 제공합니다. 객실은 잘 관리되어 있습니다.", "rating": 4.0},
                {"title": "비즈니스에 완벽", "comment": "편리한 위치. 빠른 WiFi와 편안한 업무용 책상.", "rating": 4.5}
            ],
            'zh': [
                {"title": "优秀的住宿！", "comment": "靠近车站的绝佳位置。房间干净，员工友好。", "rating": 4.5},
                {"title": "物有所值", "comment": "酒店提供极好的性价比。房间维护良好。", "rating": 4.0},
                {"title": "商务的完美选择", "comment": "位置便利。快速WiFi和舒适的办公桌。", "rating": 4.5}
            ]
        }

        reviews_per_language = count // len(languages) if languages else count

        for lang in languages:
            templates = review_templates.get(lang, review_templates['en'])
            lang_count = min(reviews_per_language, len(templates) * 10)

            for i in range(lang_count):
                template = templates[i % len(templates)]
                review_date = base_date - timedelta(days=random.randint(1, 180))

                raw_data = {
                    "id": f"expedia_demo_{hotel_id}_{lang}_{i}",
                    "title": template["title"],
                    "comment": template["comment"],
                    "rating": template["rating"],
                    "rating_details": {
                        "cleanliness": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5))),
                        "service": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5))),
                        "comfort": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5))),
                        "location": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5)))
                    },
                    "reviewer_name": f"Traveler{random.randint(1000, 9999)}",
                    "age_group": random.choice(["18-24", "25-34", "35-44", "45-54", "55+"]),
                    "gender": random.choice(["Male", "Female", None]),
                    "stay_date": review_date - timedelta(days=random.randint(3, 30)),
                    "review_date": review_date,
                    "trip_type": random.choice(["Business", "Leisure", "Family", "Couples"]),
                    "room_type": random.choice(["Standard", "Deluxe", "Suite"]),
                    "helpful_count": random.randint(0, 15),
                    "url": f"https://www.expedia.com/hotel/{hotel_id}/reviews",
                    "language": lang
                }

                review = self.normalize_review(raw_data, hotel_id, f"Expedia Hotel {hotel_id}")
                reviews.append(review)

        logger.info(f"Generated {len(reviews)} Expedia demo reviews")
        return reviews
