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
        limit: int = 100
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

        if not self.enabled:
            logger.info("Using demo data - Agoda API not enabled")
            reviews = self._generate_demo_reviews(hotel_id, limit)
        else:
            # TODO: Implement real Agoda API call
            reviews = self._generate_demo_reviews(hotel_id, limit)

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

    def _generate_demo_reviews(self, hotel_id: str, count: int) -> List[Review]:
        """Generate realistic demo reviews for Agoda."""
        reviews = []
        base_date = datetime.utcnow()

        # Agoda向けのリアルなレビューテンプレート
        demo_templates = [
            {
                "title": "Amazing hotel experience",
                "comment": "The hotel exceeded our expectations. The room was spacious and clean with a beautiful view. Staff were incredibly helpful and attentive. Highly recommended!",
                "rating": 4.8
            },
            {
                "title": "Great location and service",
                "comment": "Perfect location in the city center. Easy access to shopping and restaurants. The concierge helped us book tours and restaurants. Very satisfied with our stay.",
                "rating": 4.5
            },
            {
                "title": "Comfortable and convenient",
                "comment": "Clean and comfortable rooms with modern amenities. Breakfast buffet had good variety. WiFi was fast and reliable. Good value for the price.",
                "rating": 4.2
            },
            {
                "title": "Decent stay",
                "comment": "The hotel is okay for the price. Room was clean but a bit dated. Staff were friendly. Location is convenient for exploring the area.",
                "rating": 3.8
            },
            {
                "title": "Below expectations",
                "comment": "Room was smaller than photos suggested. Noise from the street was problematic. Check-in took longer than expected. Breakfast options were limited.",
                "rating": 2.8
            }
        ]

        for i in range(min(count, 50)):
            template = random.choice(demo_templates)
            review_date = base_date - timedelta(days=random.randint(1, 180))

            raw_data = {
                "id": f"agoda_demo_{hotel_id}_{i}",
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
                "url": f"https://www.agoda.com/hotel/{hotel_id}/reviews"
            }

            review = self.normalize_review(raw_data, hotel_id, f"Agoda Hotel {hotel_id}")
            reviews.append(review)

        logger.info(f"Generated {len(reviews)} Agoda demo reviews")
        return reviews
