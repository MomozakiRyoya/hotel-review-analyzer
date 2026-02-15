"""
OTA API Keys - Secure Configuration
環境変数から認証情報を読み込みます。
"""
import os


def get_booking_credentials():
    """
    Get Booking.com API credentials from environment variables.

    Required environment variables:
    - BOOKING_USERNAME: Booking.com API username
    - BOOKING_PASSWORD: Booking.com API password
    - BOOKING_ENABLED: "true" to enable real API calls
    """
    return {
        "url": "https://supply-xml.booking.com/review-api",
        "username": os.getenv("BOOKING_USERNAME"),
        "password": os.getenv("BOOKING_PASSWORD"),
        "enabled": os.getenv("BOOKING_ENABLED", "false").lower() == "true"
    }


def get_expedia_credentials():
    """
    Get Expedia API credentials from environment variables.

    Required environment variables:
    - EXPEDIA_API_KEY: Expedia API client ID
    - EXPEDIA_API_SECRET: Expedia API client secret
    - EXPEDIA_ENABLED: "true" to enable real API calls
    """
    return {
        "api_key": os.getenv("EXPEDIA_API_KEY"),
        "api_secret": os.getenv("EXPEDIA_API_SECRET"),
        "endpoint": os.getenv("EXPEDIA_ENDPOINT", "https://api.expediagroup.com"),
        "enabled": os.getenv("EXPEDIA_ENABLED", "false").lower() == "true"
    }


def get_agoda_credentials():
    """
    Get Agoda API credentials from environment variables.

    Required environment variables:
    - AGODA_API_KEY: Agoda API key
    - AGODA_PARTNER_ID: Agoda partner ID
    - AGODA_ENABLED: "true" to enable real API calls
    """
    return {
        "api_key": os.getenv("AGODA_API_KEY"),
        "partner_id": os.getenv("AGODA_PARTNER_ID"),
        "endpoint": os.getenv("AGODA_ENDPOINT", "https://affiliateapi.agoda.com"),
        "enabled": os.getenv("AGODA_ENABLED", "false").lower() == "true"
    }
