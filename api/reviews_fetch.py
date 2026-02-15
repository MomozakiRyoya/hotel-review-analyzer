"""
Reviews fetch endpoint for Vercel.
Fetches hotel reviews from multiple OTA platforms.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
import asyncio
from urllib.parse import parse_qs

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ota.rakuten import RakutenClient
from backend.services.ota.jalan import JalanClient
from backend.services.ota.booking import BookingClient


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to fetch reviews."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            # Extract parameters
            hotel_name = data.get('hotel_name', '')
            sources = data.get('sources', ['rakuten', 'jalan', 'booking'])
            max_reviews = data.get('max_reviews', 50)

            if not hotel_name:
                self._send_error(400, "hotel_name is required")
                return

            # Fetch reviews from OTA platforms
            reviews = asyncio.run(self._fetch_reviews(hotel_name, sources, max_reviews))

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "success": True,
                "hotel_name": hotel_name,
                "total_reviews": len(reviews),
                "reviews": [r.dict() for r in reviews]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        """Handle CORS preflight request."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    async def _fetch_reviews(self, hotel_name: str, sources: list, max_reviews: int):
        """Fetch reviews from multiple OTA platforms."""
        all_reviews = []

        # Create clients
        clients = {}
        if 'rakuten' in sources:
            clients['rakuten'] = RakutenClient()
        if 'jalan' in sources:
            clients['jalan'] = JalanClient()
        if 'booking' in sources:
            clients['booking'] = BookingClient()

        # For each OTA, search for hotel and fetch reviews
        for source, client in clients.items():
            try:
                # Step 1: Search for hotel to get hotel_id
                hotels = await client.search_hotels(hotel_name)

                if not hotels:
                    continue

                # Use the first hotel result
                hotel = hotels[0]
                hotel_id = hotel.get('id', '')

                if not hotel_id:
                    continue

                # Step 2: Fetch reviews using hotel_id
                reviews = await client.fetch_reviews(hotel_id, limit=max_reviews)
                all_reviews.extend(reviews)

            except Exception as e:
                # Skip failed requests and continue with other sources
                continue

        return all_reviews[:max_reviews]

    def _send_error(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {
            "success": False,
            "error": message
        }
        self.wfile.write(json.dumps(error_response).encode('utf-8'))
