"""
Agoda OTA client.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
import random

from backend.models.review import Review, OTASource
from backend.services.ota.base import OTAClient
from backend.services.ota.api_keys import get_agoda_credentials
from backend.utils.exceptions import HotelNotFoundError, ReviewFetchError, AuthenticationError
import httpx
from typing import Dict, Any


class AgodaClient(OTAClient):
    """Agoda client for hotel reviews."""

    def __init__(self):
        """Initialize Agoda client."""
        super().__init__()
        self.config = get_agoda_credentials()
        self.api_key = self.config.get("api_key")
        self.partner_id = self.config.get("partner_id")
        self.endpoint = self.config.get("endpoint")
        self.enabled = self.config.get("enabled", False)

        if not self.enabled:
            logger.warning("Agoda API not enabled - using demo data")

    def _get_source(self) -> OTASource:
        """Get OTA source identifier."""
        return OTASource.AGODA

    async def search_hotels(
        self,
        hotel_name: str,
        location: Optional[str] = None
    ) -> List[dict]:
        """
        Search for hotels on Agoda.

        Args:
            hotel_name: Hotel name to search
            location: Optional location filter

        Returns:
            List of hotel search results
        """
        logger.info(f"Searching Agoda for hotel: {hotel_name}")

        if not self.enabled:
            logger.info("Using demo data - Agoda API not enabled")
            return self._mock_search_hotels(hotel_name)

        # TODO: Implement real Agoda API call
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
        Fetch reviews from Agoda.

        Args:
            hotel_id: Agoda hotel ID
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum reviews to fetch

        Returns:
            List of Review objects
        """
        logger.info(f"Fetching Agoda reviews for hotel: {hotel_id}")

        if languages is None:
            languages = ['en', 'ja']

        if not self.enabled:
            logger.info("Using demo data - Agoda API not enabled")
            reviews = self._generate_demo_reviews(hotel_id, limit, languages)
        else:
            # Real Agoda API call
            try:
                logger.info("Fetching real reviews from Agoda API")
                reviews = await self._fetch_real_reviews(hotel_id, limit, languages)
            except Exception as e:
                logger.error(f"Failed to fetch real reviews: {e}, falling back to demo")
                reviews = self._generate_demo_reviews(hotel_id, limit, languages)

        # Filter by date
        reviews = self._filter_reviews_by_date(reviews, start_date, end_date)

        # Apply limit
        reviews = self._limit_reviews(reviews, limit)

        logger.info(f"Fetched {len(reviews)} reviews from Agoda")
        return reviews

    def normalize_review(
        self,
        raw_data: dict,
        hotel_id: str,
        hotel_name: str
    ) -> Review:
        """
        Normalize Agoda review data to Review model.

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
            "id": "agoda_hotel_001",
            "name": hotel_name,
            "url": "https://www.agoda.com/hotel/sample",
            "rating": 4.4,
            "review_count": 320
        }]

    async def _fetch_real_reviews(self, hotel_id: str, limit: int, languages: List[str]) -> List[Review]:
        """
        Fetch real reviews from Agoda Affiliate API.

        API: Agoda Affiliate/Partner API
        Auth: API Key authentication
        """
        if not self.api_key or not self.partner_id:
            raise AuthenticationError("Agoda API credentials not configured")

        # Agoda reviews endpoint (example - actual endpoint may vary)
        url = f"{self.endpoint}/properties/{hotel_id}/reviews"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Partner-ID": self.partner_id
        }

        params = {
            "limit": limit,
            "language": ",".join(languages) if languages else "en"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()
                reviews = []

                # Parse Agoda response format
                # Note: Actual response structure may vary
                reviews_data = data.get("reviews", data.get("data", []))

                for review_data in reviews_data[:limit]:
                    review = self._parse_agoda_review(review_data, hotel_id)
                    reviews.append(review)

                logger.info(f"Fetched {len(reviews)} real reviews from Agoda")
                return reviews

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                raise AuthenticationError(f"Agoda authentication failed: {e}")
            elif e.response.status_code == 404:
                raise HotelNotFoundError(f"Hotel {hotel_id} not found on Agoda")
            else:
                raise ReviewFetchError(f"Agoda API error: {e}")
        except httpx.RequestError as e:
            raise ReviewFetchError(f"Agoda request failed: {e}")

    def _parse_agoda_review(self, review_data: Dict[Any, Any], hotel_id: str) -> Review:
        """Parse Agoda review data into Review model."""
        # Agoda specific field mapping (adjust based on actual API response)
        raw_data = {
            "id": review_data.get("review_id", review_data.get("id", "")),
            "title": review_data.get("title", review_data.get("review_title")),
            "comment": review_data.get("comment", review_data.get("review_text", "")),
            "rating": review_data.get("rating", review_data.get("overall_rating", 0)),
            "reviewer_name": review_data.get("reviewer_name", review_data.get("guest_name")),
            "review_date": review_data.get("review_date", review_data.get("created_date")),
            "stay_date": review_data.get("stay_date", review_data.get("check_out_date")),
            "trip_type": review_data.get("trip_type", review_data.get("travel_purpose")),
            "room_type": review_data.get("room_type"),
            "url": f"https://www.agoda.com/hotel/{hotel_id}/reviews"
        }

        return self.normalize_review(raw_data, hotel_id, review_data.get("hotel_name", ""))

    def _generate_demo_reviews(self, hotel_id: str, count: int, languages: List[str]) -> List[Review]:
        """Generate realistic demo reviews for Agoda."""
        reviews = []
        base_date = datetime.utcnow()

        # Multi-language review templates
        review_templates = {
            'en': [
                {"title": "Amazing experience", "comment": "The hotel exceeded our expectations. Spacious and clean. Highly recommended!", "rating": 4.8},
                {"title": "Great location", "comment": "Perfect location in city center. Easy access to shopping and restaurants.", "rating": 4.5},
                {"title": "Comfortable stay", "comment": "Clean rooms with modern amenities. Good value for the price.", "rating": 4.2}
            ],
            'ja': [
                {"title": "素晴らしい体験", "comment": "ホテルは期待を超えました。広くて清潔。強くお勧めします！", "rating": 4.8},
                {"title": "素晴らしい立地", "comment": "市内中心部の完璧な立地。ショッピングやレストランへのアクセスが簡単。", "rating": 4.5},
                {"title": "快適な滞在", "comment": "モダンな設備の清潔な部屋。価格に見合った価値。", "rating": 4.2}
            ],
            'ko': [
                {"title": "놀라운 경험", "comment": "호텔은 우리의 기대를 뛰어넘었습니다. 넓고 깨끗합니다. 강력 추천!", "rating": 4.8},
                {"title": "훌륭한 위치", "comment": "도심의 완벽한 위치. 쇼핑과 레스토랑 접근이 쉽습니다.", "rating": 4.5},
                {"title": "편안한 숙박", "comment": "현대적인 편의시설이 있는 깨끗한 객실. 가격 대비 좋은 가치.", "rating": 4.2}
            ],
            'zh': [
                {"title": "惊人的体验", "comment": "酒店超出了我们的期望。宽敞干净。强烈推荐！", "rating": 4.8},
                {"title": "绝佳位置", "comment": "市中心的完美位置。购物和餐厅交通便利。", "rating": 4.5},
                {"title": "舒适的住宿", "comment": "配备现代设施的干净房间。物有所值。", "rating": 4.2}
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
                    "id": f"agoda_demo_{hotel_id}_{lang}_{i}",
                    "title": template["title"],
                    "comment": template["comment"],
                    "rating": template["rating"],
                    "rating_details": {
                        "cleanliness": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5))),
                        "facilities": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5))),
                        "staff": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5))),
                        "value_for_money": max(1, min(5, template["rating"] + random.uniform(-0.5, 0.5)))
                    },
                    "reviewer_name": f"Guest{random.randint(1000, 9999)}",
                    "age_group": random.choice(["18-24", "25-34", "35-44", "45-54", "55+"]),
                    "gender": random.choice(["Male", "Female", None]),
                    "stay_date": review_date - timedelta(days=random.randint(3, 30)),
                    "review_date": review_date,
                    "trip_type": random.choice(["Business", "Leisure", "Family", "Solo", "Couples"]),
                    "room_type": random.choice(["Standard Room", "Deluxe Room", "Suite", "Superior Room"]),
                    "helpful_count": random.randint(0, 20),
                    "url": f"https://www.agoda.com/hotel/{hotel_id}/reviews",
                    "language": lang
                }

                review = self.normalize_review(raw_data, hotel_id, f"Agoda Hotel {hotel_id}")
                reviews.append(review)

        logger.info(f"Generated {len(reviews)} Agoda demo reviews")
        return reviews
