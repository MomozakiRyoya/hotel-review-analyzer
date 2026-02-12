"""
Abstract base class for OTA clients.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import httpx
from loguru import logger

from backend.models.review import Review, OTASource
from backend.config import settings
from backend.utils.helpers import retry_async, rate_limit


class OTAClient(ABC):
    """Abstract base class for OTA API/scraping clients."""

    def __init__(self):
        """Initialize OTA client."""
        self.source: OTASource = self._get_source()
        self.client: Optional[httpx.AsyncClient] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    @abstractmethod
    def _get_source(self) -> OTASource:
        """
        Get the OTA source identifier.

        Returns:
            OTASource: Source identifier
        """
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            follow_redirects=True
        )
        logger.info(f"{self.source.value} client initialized")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
            logger.info(f"{self.source.value} client closed")

    @abstractmethod
    async def search_hotels(
        self,
        hotel_name: str,
        location: Optional[str] = None
    ) -> List[dict]:
        """
        Search for hotels by name.

        Args:
            hotel_name: Hotel name to search
            location: Optional location filter

        Returns:
            List of hotel search results with id and name

        Raises:
            HotelNotFoundError: If no hotels found
            OTAException: If search fails
        """
        pass

    @abstractmethod
    async def fetch_reviews(
        self,
        hotel_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Review]:
        """
        Fetch reviews for a specific hotel.

        Args:
            hotel_id: Hotel ID from the OTA platform
            start_date: Start date for review filtering (optional)
            end_date: End date for review filtering (optional)
            limit: Maximum number of reviews to fetch

        Returns:
            List of normalized Review objects

        Raises:
            ReviewFetchError: If fetching reviews fails
            OTAException: If general error occurs
        """
        pass

    @abstractmethod
    def normalize_review(self, raw_data: dict, hotel_id: str, hotel_name: str) -> Review:
        """
        Normalize raw OTA review data to Review model.

        Args:
            raw_data: Raw review data from OTA
            hotel_id: Hotel ID
            hotel_name: Hotel name

        Returns:
            Normalized Review object
        """
        pass

    @rate_limit()
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with rate limiting and retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            Response object

        Raises:
            APIRateLimitError: If rate limit exceeded
            OTAException: If request fails
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        async def _request():
            logger.debug(f"{self.source.value} {method} {url}")
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        try:
            return await retry_async(
                _request,
                max_retries=settings.max_retries,
                exceptions=(httpx.HTTPError,)
            )
        except Exception as e:
            logger.error(f"{self.source.value} request failed: {str(e)}")
            raise

    def _filter_reviews_by_date(
        self,
        reviews: List[Review],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Review]:
        """
        Filter reviews by date range.

        Args:
            reviews: List of reviews
            start_date: Start date filter
            end_date: End date filter

        Returns:
            Filtered list of reviews
        """
        filtered = reviews

        if start_date:
            filtered = [r for r in filtered if r.review_date >= start_date]

        if end_date:
            filtered = [r for r in filtered if r.review_date <= end_date]

        logger.info(
            f"{self.source.value} filtered {len(reviews)} -> {len(filtered)} reviews "
            f"(date range: {start_date} to {end_date})"
        )

        return filtered

    def _limit_reviews(self, reviews: List[Review], limit: int) -> List[Review]:
        """
        Limit number of reviews.

        Args:
            reviews: List of reviews
            limit: Maximum number of reviews

        Returns:
            Limited list of reviews
        """
        if len(reviews) > limit:
            logger.info(f"{self.source.value} limiting {len(reviews)} -> {limit} reviews")
            return reviews[:limit]
        return reviews
