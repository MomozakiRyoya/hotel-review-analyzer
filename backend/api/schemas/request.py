"""
API request schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReviewFetchRequest(BaseModel):
    """Request schema for fetching reviews."""

    hotel_name: str = Field(..., description="Hotel name to search")
    ota_sources: List[str] = Field(
        ...,
        description="List of OTA sources (rakuten, jalan, booking)"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Start date for review filtering"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for review filtering"
    )
    limit_per_ota: int = Field(
        100,
        ge=1,
        le=500,
        description="Maximum reviews per OTA"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hotel_name": "東京ホテル",
                "ota_sources": ["rakuten", "jalan"],
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2025-01-15T23:59:59",
                "limit_per_ota": 100
            }
        }


class AnalyzeRequest(BaseModel):
    """Request schema for analyzing reviews."""

    review_ids: Optional[List[str]] = Field(
        None,
        description="Specific review IDs to analyze (if None, analyze all)"
    )
    include_keywords: bool = Field(
        True,
        description="Include keyword extraction"
    )
    include_sentiment: bool = Field(
        True,
        description="Include sentiment analysis"
    )
    keyword_limit: int = Field(
        30,
        ge=5,
        le=100,
        description="Number of top keywords to extract"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "include_keywords": True,
                "include_sentiment": True,
                "keyword_limit": 30
            }
        }


class ExportRequest(BaseModel):
    """Request schema for exporting to Excel."""

    hotel_name: str = Field(..., description="Hotel name for the report")
    include_charts: bool = Field(
        True,
        description="Include charts in Excel"
    )
    include_raw_data: bool = Field(
        True,
        description="Include raw review data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hotel_name": "東京ホテル",
                "include_charts": True,
                "include_raw_data": True
            }
        }
