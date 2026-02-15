"""
Review API endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import asyncio
import time
from datetime import datetime
from loguru import logger

from backend.api.schemas.request import ReviewFetchRequest, AnalyzeRequest, ExportRequest
from backend.api.schemas.response import ReviewFetchResponse, AnalyzeResponse, ExportResponse, ErrorResponse
from backend.models.review import Review, ReviewStats, OTASource
from backend.models.analysis_result import AnalysisResult, OTAAnalysis, SentimentTrend
from backend.services.ota.booking import BookingClient
from backend.services.ota.expedia import ExpediaClient
from backend.services.ota.agoda import AgodaClient
import os

# Use lightweight version for Vercel deployment
if os.environ.get('VERCEL'):
    from backend.services.analyzer.sentiment_lite import SentimentAnalyzerLite as SentimentAnalyzer
else:
    try:
        from backend.services.analyzer.sentiment import SentimentAnalyzer
    except ImportError:
        from backend.services.analyzer.sentiment_lite import SentimentAnalyzerLite as SentimentAnalyzer

from backend.services.analyzer.keyword import KeywordExtractor
from backend.services.excel.generator import ExcelReportGenerator
from backend.utils.exceptions import OTAException, AnalysisException, ExcelGenerationException


router = APIRouter()

# Global storage for reviews and analysis (in production, use database)
_reviews_storage: List[Review] = []
_analysis_result_storage: Optional[AnalysisResult] = None


# OTA client mapping
OTA_CLIENTS = {
    "booking": BookingClient,
    "expedia": ExpediaClient,
    "agoda": AgodaClient
}


@router.post("/fetch", response_model=ReviewFetchResponse)
async def fetch_reviews(request: ReviewFetchRequest):
    """
    Fetch reviews from multiple OTA platforms.

    Args:
        request: Review fetch request parameters

    Returns:
        ReviewFetchResponse with fetched reviews

    Raises:
        HTTPException: If fetching fails
    """
    logger.info(f"Fetching reviews for hotel: {request.hotel_name}")
    logger.info(f"OTA sources: {request.ota_sources}")
    logger.info(f"Date range: {request.start_date} to {request.end_date}")

    start_time = time.time()
    all_reviews: List[Review] = []
    reviews_by_ota = {}

    try:
        # Fetch reviews from each OTA in parallel
        tasks = []
        for ota_source in request.ota_sources:
            if ota_source not in OTA_CLIENTS:
                logger.warning(f"Unknown OTA source: {ota_source}")
                continue

            task = _fetch_from_ota(
                ota_source=ota_source,
                hotel_name=request.hotel_name,
                start_date=request.start_date,
                end_date=request.end_date,
                limit=request.limit_per_ota
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            ota_source = request.ota_sources[i]

            if isinstance(result, Exception):
                logger.error(f"Failed to fetch from {ota_source}: {str(result)}")
                reviews_by_ota[ota_source] = 0
            else:
                reviews = result
                all_reviews.extend(reviews)
                reviews_by_ota[ota_source] = len(reviews)
                logger.info(f"Fetched {len(reviews)} reviews from {ota_source}")

        # Store reviews globally (in production, save to database)
        global _reviews_storage
        _reviews_storage = all_reviews

        # Calculate statistics
        stats = _calculate_stats(all_reviews)

        fetch_time = time.time() - start_time
        logger.info(f"Total reviews fetched: {len(all_reviews)} in {fetch_time:.2f}s")

        return ReviewFetchResponse(
            success=True,
            message=f"Successfully fetched {len(all_reviews)} reviews from {len(request.ota_sources)} OTA sources",
            total_reviews=len(all_reviews),
            reviews_by_ota=reviews_by_ota,
            reviews=all_reviews,
            stats=stats,
            fetch_time=fetch_time
        )

    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="ReviewFetchError",
                message=str(e)
            ).model_dump()
        )


async def _fetch_from_ota(
    ota_source: str,
    hotel_name: str,
    start_date,
    end_date,
    limit: int
) -> List[Review]:
    """
    Fetch reviews from a specific OTA.

    Args:
        ota_source: OTA source name
        hotel_name: Hotel name
        start_date: Start date filter
        end_date: End date filter
        limit: Maximum reviews

    Returns:
        List of reviews
    """
    client_class = OTA_CLIENTS[ota_source]

    async with client_class() as client:
        # Search for hotel
        hotels = await client.search_hotels(hotel_name)

        if not hotels:
            logger.warning(f"No hotels found on {ota_source} for: {hotel_name}")
            return []

        # Use first hotel from search results
        hotel = hotels[0]
        hotel_id = hotel["id"]

        # Fetch reviews
        reviews = await client.fetch_reviews(
            hotel_id=hotel_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return reviews


def _calculate_stats(reviews: List[Review]) -> ReviewStats:
    """
    Calculate statistics from reviews.

    Args:
        reviews: List of reviews

    Returns:
        ReviewStats object
    """
    if not reviews:
        return ReviewStats(
            total_reviews=0,
            average_rating=0,
            sentiment_distribution={},
            rating_distribution={},
            reviews_by_ota={},
            date_range={}
        )

    # Calculate average rating
    total_rating = sum(r.rating for r in reviews)
    average_rating = total_rating / len(reviews)

    # Sentiment distribution (will be populated after analysis)
    sentiment_distribution = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }

    # Rating distribution
    rating_distribution = {}
    for review in reviews:
        rating_key = str(int(review.rating))
        rating_distribution[rating_key] = rating_distribution.get(rating_key, 0) + 1

    # Reviews by OTA
    reviews_by_ota = {}
    for review in reviews:
        ota = review.source.value
        reviews_by_ota[ota] = reviews_by_ota.get(ota, 0) + 1

    # Date range
    review_dates = [r.review_date for r in reviews]
    date_range = {
        "earliest": min(review_dates).isoformat() if review_dates else None,
        "latest": max(review_dates).isoformat() if review_dates else None
    }

    return ReviewStats(
        total_reviews=len(reviews),
        average_rating=round(average_rating, 2),
        sentiment_distribution=sentiment_distribution,
        rating_distribution=rating_distribution,
        reviews_by_ota=reviews_by_ota,
        date_range=date_range
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_reviews(request: AnalyzeRequest):
    """
    Analyze reviews with sentiment analysis and keyword extraction.

    Args:
        request: Analysis request parameters

    Returns:
        AnalyzeResponse with analysis results

    Raises:
        HTTPException: If analysis fails or no reviews available
    """
    global _reviews_storage

    if not _reviews_storage:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="NoReviewsError",
                message="No reviews available. Please fetch reviews first using /api/reviews/fetch"
            ).model_dump()
        )

    logger.info(f"Analyzing {len(_reviews_storage)} reviews")
    start_time = time.time()

    try:
        # Initialize analyzers
        sentiment_analyzer = SentimentAnalyzer()
        keyword_extractor = KeywordExtractor()

        reviews = _reviews_storage.copy()

        # Perform sentiment analysis if requested
        if request.include_sentiment:
            logger.info("Performing sentiment analysis...")
            reviews = sentiment_analyzer.analyze_reviews(reviews)
            _reviews_storage = reviews  # Update storage with sentiment data

        # Extract keywords if requested
        top_keywords = []
        positive_keywords = []
        negative_keywords = []

        if request.include_keywords:
            logger.info("Extracting keywords...")
            top_keywords = keyword_extractor.extract_keywords_from_reviews(
                reviews,
                top_n=request.keyword_limit
            )

            # Extract positive/negative keywords
            positive_keywords = keyword_extractor.extract_by_sentiment(
                reviews,
                sentiment="positive",
                top_n=10
            )
            negative_keywords = keyword_extractor.extract_by_sentiment(
                reviews,
                sentiment="negative",
                top_n=10
            )

        # Build analysis result
        result = _build_analysis_result(
            reviews=reviews,
            top_keywords=top_keywords,
            positive_keywords=positive_keywords,
            negative_keywords=negative_keywords,
            sentiment_analyzer=sentiment_analyzer,
            keyword_extractor=keyword_extractor
        )

        processing_time = time.time() - start_time
        result.processing_time = round(processing_time, 2)

        # Store analysis result globally
        global _analysis_result_storage
        _analysis_result_storage = result

        logger.info(f"✅ Analysis complete in {processing_time:.2f}s")

        return AnalyzeResponse(
            success=True,
            message=f"Successfully analyzed {len(reviews)} reviews",
            analysis_result=result
        )

    except AnalysisException as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=type(e).__name__,
                message=str(e)
            ).model_dump()
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="AnalysisError",
                message=str(e)
            ).model_dump()
        )


def _build_analysis_result(
    reviews: List[Review],
    top_keywords: List,
    positive_keywords: List,
    negative_keywords: List,
    sentiment_analyzer: SentimentAnalyzer,
    keyword_extractor: KeywordExtractor
) -> AnalysisResult:
    """
    Build complete analysis result.

    Args:
        reviews: Analyzed reviews
        top_keywords: Top keywords overall
        positive_keywords: Top positive keywords
        negative_keywords: Top negative keywords
        sentiment_analyzer: Sentiment analyzer instance
        keyword_extractor: Keyword extractor instance

    Returns:
        AnalysisResult object
    """
    # Overall statistics
    sentiment_dist = sentiment_analyzer.get_sentiment_distribution(reviews)
    avg_sentiment = sentiment_analyzer.get_average_sentiment(reviews)

    # Rating distribution
    rating_dist = {}
    for review in reviews:
        rating_key = str(int(review.rating))
        rating_dist[rating_key] = rating_dist.get(rating_key, 0) + 1

    # Date range
    review_dates = [r.review_date for r in reviews]
    start_date = min(review_dates) if review_dates else datetime.utcnow()
    end_date = max(review_dates) if review_dates else datetime.utcnow()

    # Average rating
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

    # OTA breakdown
    ota_analyses = _build_ota_analyses(reviews, keyword_extractor)

    # Build result
    return AnalysisResult(
        total_reviews=len(reviews),
        average_rating=round(avg_rating, 2),
        average_sentiment=avg_sentiment,
        start_date=start_date,
        end_date=end_date,
        sentiment_distribution=sentiment_dist,
        rating_distribution=rating_dist,
        top_keywords=top_keywords,
        positive_keywords=positive_keywords,
        negative_keywords=negative_keywords,
        ota_analyses=ota_analyses,
        sentiment_trend=[],  # TODO: Implement trend calculation
        processing_time=0  # Will be set by caller
    )


def _build_ota_analyses(
    reviews: List[Review],
    keyword_extractor: KeywordExtractor
) -> List[OTAAnalysis]:
    """
    Build OTA-specific analyses.

    Args:
        reviews: All reviews
        keyword_extractor: Keyword extractor instance

    Returns:
        List of OTAAnalysis objects
    """
    ota_analyses = []

    # Group reviews by OTA
    reviews_by_ota = {}
    for review in reviews:
        ota = review.source.value
        if ota not in reviews_by_ota:
            reviews_by_ota[ota] = []
        reviews_by_ota[ota].append(review)

    # Analyze each OTA
    for ota_name, ota_reviews in reviews_by_ota.items():
        # Calculate statistics
        avg_rating = sum(r.rating for r in ota_reviews) / len(ota_reviews)
        avg_sentiment = sum(
            r.sentiment_score for r in ota_reviews
            if r.sentiment_score is not None
        ) / len(ota_reviews) if ota_reviews else 0

        # Sentiment counts
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for review in ota_reviews:
            if review.sentiment:
                sentiment_counts[review.sentiment] += 1

        # Rating distribution
        rating_dist = {}
        for review in ota_reviews:
            rating_key = str(int(review.rating))
            rating_dist[rating_key] = rating_dist.get(rating_key, 0) + 1

        # Top keywords for this OTA
        top_keywords = keyword_extractor.extract_keywords_from_reviews(
            ota_reviews,
            top_n=10
        )

        ota_analyses.append(
            OTAAnalysis(
                ota_name=ota_name,
                total_reviews=len(ota_reviews),
                average_rating=round(avg_rating, 2),
                average_sentiment=round(avg_sentiment, 3),
                positive_count=sentiment_counts["positive"],
                neutral_count=sentiment_counts["neutral"],
                negative_count=sentiment_counts["negative"],
                rating_distribution=rating_dist,
                top_keywords=top_keywords,
                sentiment_trend=[]  # TODO: Implement trend
            )
        )

    return ota_analyses


@router.post("/export", response_model=ExportResponse)
async def export_to_excel(request: ExportRequest):
    """
    Export analysis results to Excel file.

    Args:
        request: Export request parameters

    Returns:
        ExportResponse with file information

    Raises:
        HTTPException: If export fails or no data available
    """
    global _reviews_storage, _analysis_result_storage

    if not _reviews_storage:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="NoReviewsError",
                message="No reviews available. Please fetch reviews first."
            ).model_dump()
        )

    if not _analysis_result_storage:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="NoAnalysisError",
                message="No analysis results available. Please run analysis first."
            ).model_dump()
        )

    logger.info(f"Exporting analysis to Excel: {request.hotel_name}")
    start_time = time.time()

    try:
        # Initialize Excel generator
        generator = ExcelReportGenerator()

        # Generate report
        filepath = generator.generate_report(
            reviews=_reviews_storage,
            analysis_result=_analysis_result_storage,
            hotel_name=request.hotel_name,
            include_charts=request.include_charts,
            include_raw_data=request.include_raw_data
        )

        # Get file info
        file_stat = filepath.stat()
        export_time = time.time() - start_time

        logger.info(f"✅ Excel exported: {filepath.name} ({file_stat.st_size} bytes)")

        return ExportResponse(
            success=True,
            message=f"Excel report generated successfully",
            file_path=str(filepath),
            file_size=file_stat.st_size,
            export_time=round(export_time, 2)
        )

    except ExcelGenerationException as e:
        logger.error(f"Excel export failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="ExcelGenerationError",
                message=str(e)
            ).model_dump()
        )
    except Exception as e:
        logger.error(f"Unexpected error during export: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="ExportError",
                message=str(e)
            ).model_dump()
        )
