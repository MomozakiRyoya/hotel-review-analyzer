"""
API response schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from backend.models.review import Review, ReviewStats
from backend.models.analysis_result import AnalysisResult


class ReviewFetchResponse(BaseModel):
    """Response schema for review fetch endpoint."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Response message")
    total_reviews: int = Field(..., description="Total reviews fetched")
    reviews_by_ota: dict = Field(..., description="Review count by OTA")
    reviews: List[Review] = Field(..., description="List of fetched reviews")
    stats: Optional[ReviewStats] = Field(None, description="Review statistics")
    fetch_time: float = Field(..., description="Time taken to fetch reviews (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully fetched reviews",
                "total_reviews": 150,
                "reviews_by_ota": {
                    "rakuten": 60,
                    "jalan": 50,
                    "booking": 40
                },
                "fetch_time": 5.2
            }
        }


class AnalyzeResponse(BaseModel):
    """Response schema for analysis endpoint."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Response message")
    analysis_result: AnalysisResult = Field(..., description="Analysis results")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Analysis completed successfully"
            }
        }


class ExportResponse(BaseModel):
    """Response schema for export endpoint."""

    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Response message")
    file_path: str = Field(..., description="Path to exported Excel file")
    file_size: int = Field(..., description="File size in bytes")
    export_time: float = Field(..., description="Time taken to export (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Excel report generated successfully",
                "file_path": "./output/hotel_review_report_20250115.xlsx",
                "file_size": 1048576,
                "export_time": 2.5
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ReviewFetchError",
                "message": "Failed to fetch reviews from Jalan",
                "details": {
                    "ota": "jalan",
                    "reason": "Connection timeout"
                }
            }
        }
