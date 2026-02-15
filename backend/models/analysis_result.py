"""
Analysis result models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class KeywordResult(BaseModel):
    """Keyword extraction result."""

    keyword: str = Field(..., description="Extracted keyword")
    frequency: int = Field(..., description="Frequency count")
    score: float = Field(..., description="TF-IDF-like importance score")
    category: Optional[str] = Field(None, description="Category (positive/negative/neutral)")

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "清潔",
                "frequency": 45,
                "score": 0.82,
                "category": "positive"
            }
        }


class SentimentTrend(BaseModel):
    """Sentiment trend over time."""

    date: datetime = Field(..., description="Date")
    average_sentiment: float = Field(..., description="Average sentiment score")
    review_count: int = Field(..., description="Number of reviews")
    positive_count: int = Field(0, description="Positive reviews")
    neutral_count: int = Field(0, description="Neutral reviews")
    negative_count: int = Field(0, description="Negative reviews")


class OTAAnalysis(BaseModel):
    """Analysis results for a specific OTA."""

    ota_name: str = Field(..., description="OTA platform name")
    total_reviews: int = Field(..., description="Total reviews")
    average_rating: float = Field(..., description="Average rating")
    average_sentiment: float = Field(..., description="Average sentiment score")

    # Sentiment breakdown
    positive_count: int = Field(..., description="Number of positive reviews")
    neutral_count: int = Field(..., description="Number of neutral reviews")
    negative_count: int = Field(..., description="Number of negative reviews")

    # Rating distribution
    rating_distribution: Dict[str, int] = Field(
        ...,
        description="Distribution of ratings"
    )

    # Top keywords
    top_keywords: List[KeywordResult] = Field(
        default_factory=list,
        description="Top keywords for this OTA"
    )

    # Sentiment trend
    sentiment_trend: List[SentimentTrend] = Field(
        default_factory=list,
        description="Sentiment trend over time"
    )


class AnalysisResult(BaseModel):
    """Complete analysis result."""

    # Summary
    total_reviews: int = Field(..., description="Total number of reviews")
    average_rating: float = Field(..., description="Overall average rating")
    average_sentiment: float = Field(..., description="Overall average sentiment score")

    # Date range
    start_date: datetime = Field(..., description="Earliest review date")
    end_date: datetime = Field(..., description="Latest review date")

    # Sentiment distribution
    sentiment_distribution: Dict[str, int] = Field(
        ...,
        description="Overall sentiment distribution"
    )

    # Rating distribution
    rating_distribution: Dict[str, int] = Field(
        ...,
        description="Overall rating distribution"
    )

    # Top keywords (across all OTAs)
    top_keywords: List[KeywordResult] = Field(
        ...,
        description="Top 30 keywords overall"
    )

    # Positive and negative keywords
    positive_keywords: List[KeywordResult] = Field(
        default_factory=list,
        description="Top positive keywords"
    )
    negative_keywords: List[KeywordResult] = Field(
        default_factory=list,
        description="Top negative keywords"
    )

    # OTA breakdown
    ota_analyses: List[OTAAnalysis] = Field(
        default_factory=list,
        description="Analysis per OTA"
    )

    # Overall sentiment trend
    sentiment_trend: List[SentimentTrend] = Field(
        default_factory=list,
        description="Overall sentiment trend over time"
    )

    # Processing metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_reviews": 150,
                "average_rating": 4.2,
                "average_sentiment": 0.65,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2025-01-15T00:00:00",
                "sentiment_distribution": {
                    "positive": 100,
                    "neutral": 30,
                    "negative": 20
                },
                "rating_distribution": {
                    "5": 65,
                    "4": 50,
                    "3": 20,
                    "2": 10,
                    "1": 5
                },
                "top_keywords": [
                    {
                        "keyword": "清潔",
                        "frequency": 45,
                        "score": 0.82,
                        "category": "positive"
                    }
                ],
                "processing_time": 12.5
            }
        }
