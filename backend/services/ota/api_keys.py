"""
OTA API Keys - Hardcoded Configuration
このファイルは環境変数ではなく、プログラム側で直接管理します。
"""

# Booking.com API Credentials
BOOKING_API_CONFIG = {
    "url": "https://distribution-xml.booking.com/2.7/json/reviews",
    "username": "YOUR_BOOKING_USERNAME",  # 実際のユーザー名に置き換え
    "password": "YOUR_BOOKING_PASSWORD",  # 実際のパスワードに置き換え
    "enabled": False  # 本番環境で有効化する場合はTrue
}

# Expedia API Credentials
EXPEDIA_API_CONFIG = {
    "api_key": "YOUR_EXPEDIA_API_KEY",  # 実際のAPIキーに置き換え
    "api_secret": "YOUR_EXPEDIA_API_SECRET",  # 実際のシークレットに置き換え
    "endpoint": "https://api.expedia.com/reviews/v3",
    "enabled": False  # 本番環境で有効化する場合はTrue
}

# Agoda API Credentials
AGODA_API_CONFIG = {
    "api_key": "YOUR_AGODA_API_KEY",  # 実際のAPIキーに置き換え
    "partner_id": "YOUR_AGODA_PARTNER_ID",  # 実際のパートナーIDに置き換え
    "endpoint": "https://affiliateapi.agoda.com/reviews",
    "enabled": False  # 本番環境で有効化する場合はTrue
}


def get_booking_credentials():
    """Get Booking.com API credentials."""
    return BOOKING_API_CONFIG


def get_expedia_credentials():
    """Get Expedia API credentials."""
    return EXPEDIA_API_CONFIG


def get_agoda_credentials():
    """Get Agoda API credentials."""
    return AGODA_API_CONFIG
