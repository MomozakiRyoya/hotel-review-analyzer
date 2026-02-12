"""
Custom exceptions for the Hotel Review Analyzer application.
"""


class HotelReviewAnalyzerException(Exception):
    """Base exception for all application errors."""
    pass


# OTA Related Exceptions
class OTAException(HotelReviewAnalyzerException):
    """Base exception for OTA-related errors."""
    pass


class APIRateLimitError(OTAException):
    """Raised when API rate limit is exceeded."""
    pass


class AuthenticationError(OTAException):
    """Raised when API authentication fails."""
    pass


class HotelNotFoundError(OTAException):
    """Raised when specified hotel is not found."""
    pass


class ReviewFetchError(OTAException):
    """Raised when review fetching fails."""
    pass


# Analysis Related Exceptions
class AnalysisException(HotelReviewAnalyzerException):
    """Base exception for analysis-related errors."""
    pass


class SentimentAnalysisError(AnalysisException):
    """Raised when sentiment analysis fails."""
    pass


class KeywordExtractionError(AnalysisException):
    """Raised when keyword extraction fails."""
    pass


# Excel Generation Exceptions
class ExcelGenerationException(HotelReviewAnalyzerException):
    """Base exception for Excel generation errors."""
    pass


class SheetCreationError(ExcelGenerationException):
    """Raised when sheet creation fails."""
    pass


class ChartCreationError(ExcelGenerationException):
    """Raised when chart creation fails."""
    pass
