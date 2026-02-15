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
        limit: int = 100
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

        if not self.enabled:
            logger.info("Using demo data - Booking.com API not enabled")
            reviews = self._generate_mock_reviews(hotel_id, limit)
        else:
            # TODO: Implement real Booking.com API call
            reviews = self._generate_mock_reviews(hotel_id, limit)

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

    def _generate_mock_reviews(self, hotel_id: str, count: int) -> List[Review]:
        """
        Generate mock reviews for testing.

        Args:
            hotel_id: Hotel ID
            count: Number of reviews to generate

        Returns:
            List of mock Review objects
        """
        mock_comments = [
            "Excellent hotel with great service. The staff was very helpful and friendly.",
            "Clean rooms and good location. Would definitely stay again.",
            "The breakfast was amazing. Room was spacious and comfortable.",
            "Good value for money. Location is perfect for sightseeing.",
            "Room was a bit small but overall good experience.",
            "Staff went above and beyond to make our stay comfortable.",
            "Beautiful views from the room. Very relaxing atmosphere.",
            "WiFi could be better, but everything else was great.",
            "Perfect for families. Kids loved the facilities.",
            "Outstanding experience. Highly recommended!"
        ]

        reviews = []
        base_date = datetime.utcnow()

        for i in range(min(count, 10)):  # Limit mock data to 10
            # Booking.com uses 10-point scale
            rating_10_scale = random.choice([7, 7.5, 8, 8, 8.5, 9, 9, 9.5, 10])
            review_date = base_date - timedelta(days=random.randint(1, 365))

            raw_data = {
                "id": f"booking_rev_{hotel_id}_{i}",
                "title": "Great stay" if i % 2 == 0 else None,
                "comment": random.choice(mock_comments),
                "rating": rating_10_scale,
                "rating_details": {
                    "cleanliness": random.uniform(7, 10),
                    "comfort": random.uniform(7, 10),
                    "location": random.uniform(7, 10),
                    "facilities": random.uniform(7, 10),
                    "staff": random.uniform(8, 10),
                    "value_for_money": random.uniform(7, 10)
                },
                "reviewer_name": f"Guest_{i}",
                "age_group": random.choice(["25-34", "35-44", "45-54", "55+"]),
                "gender": random.choice(["Male", "Female", None]),
                "stay_date": review_date - timedelta(days=random.randint(5, 20)),
                "review_date": review_date,
                "trip_type": random.choice(["Leisure", "Business", "Family", "Couple"]),
                "room_type": random.choice(["Standard Room", "Deluxe Room", "Suite"]),
                "helpful_count": random.randint(0, 20),
                "url": f"https://www.booking.com/hotel/jp/{hotel_id}.html"
            }

            review = self.normalize_review(raw_data, hotel_id, f"Sample Hotel {hotel_id}")
            reviews.append(review)

        return reviews
