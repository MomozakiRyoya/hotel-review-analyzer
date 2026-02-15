"""
Review data model.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class OTASource(str, Enum):
    """OTA platform source."""
    BOOKING = "booking"
    EXPEDIA = "expedia"
    AGODA = "agoda"


class Review(BaseModel):
    """Normalized review data model across all OTA platforms."""

    # Identifiers
    review_id: str = Field(..., description="Unique review ID from OTA")
    hotel_id: str = Field(..., description="Hotel ID from OTA")
    hotel_name: str = Field(..., description="Hotel name")

    # OTA Source
    source: OTASource = Field(..., description="OTA platform source")

    # Review Content
    title: Optional[str] = Field(None, description="Review title")
    comment: str = Field(..., description="Review comment text")

    # Ratings
    rating: float = Field(..., ge=0, le=5, description="Overall rating (0-5 scale)")
    rating_details: Optional[dict] = Field(
        None,
        description="Detailed ratings (e.g., cleanliness, location, service)"
    )

    # Reviewer Information
    reviewer_name: Optional[str] = Field(None, description="Reviewer name (anonymized)")
    reviewer_age_group: Optional[str] = Field(None, description="Age group")
    reviewer_gender: Optional[str] = Field(None, description="Gender")

    # Stay Information
    stay_date: Optional[datetime] = Field(None, description="Date of stay")
    review_date: datetime = Field(..., description="Date review was posted")

    # Trip Information
    trip_type: Optional[str] = Field(None, description="Type of trip (business, leisure, etc.)")
    room_type: Optional[str] = Field(None, description="Room type stayed")

    # Helpfulness
    helpful_count: Optional[int] = Field(0, description="Number of helpful votes")

    # Analysis Results (populated later)
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = Field(
        None,
        description="Sentiment classification"
    )
    sentiment_score: Optional[float] = Field(
        None,
        ge=-1,
        le=1,
        description="Sentiment score (-1 to 1)"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Confidence of sentiment prediction"
    )

    # Metadata
    url: Optional[str] = Field(None, description="URL to original review")
    raw_data: Optional[dict] = Field(None, description="Original raw data from OTA")

    class Config:
        json_schema_extra = {
            "example": {
                "review_id": "rev_12345",
                "hotel_id": "hotel_001",
                "hotel_name": "東京ホテル",
                "source": "rakuten",
                "title": "素晴らしい滞在でした",
                "comment": "部屋がとても綺麗で、スタッフの対応も素晴らしかったです。",
                "rating": 4.5,
                "rating_details": {
                    "cleanliness": 5,
                    "location": 4,
                    "service": 5
                },
                "reviewer_name": "田中様",
                "stay_date": "2025-01-10T00:00:00",
                "review_date": "2025-01-15T10:30:00",
                "trip_type": "leisure",
                "sentiment": "positive",
                "sentiment_score": 0.85
            }
        }


class ReviewStats(BaseModel):
    """Review statistics."""

    total_reviews: int = Field(..., description="Total number of reviews")
    average_rating: float = Field(..., description="Average rating")
    sentiment_distribution: dict = Field(
        ...,
        description="Distribution of sentiments"
    )
    rating_distribution: dict = Field(
        ...,
        description="Distribution of ratings (1-5)"
    )
    reviews_by_ota: dict = Field(
        ...,
        description="Count of reviews by OTA source"
    )
    date_range: dict = Field(
        ...,
        description="Date range of reviews"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_reviews": 150,
                "average_rating": 4.2,
                "sentiment_distribution": {
                    "positive": 100,
                    "neutral": 30,
                    "negative": 20
                },
                "rating_distribution": {
                    "1": 5,
                    "2": 10,
                    "3": 20,
                    "4": 50,
                    "5": 65
                },
                "reviews_by_ota": {
                    "rakuten": 60,
                    "jalan": 50,
                    "booking": 40
                },
                "date_range": {
                    "earliest": "2024-01-01T00:00:00",
                    "latest": "2025-01-15T00:00:00"
                }
            }
        }
