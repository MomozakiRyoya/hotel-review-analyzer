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
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.services.ota.booking import BookingClient
    from backend.services.ota.expedia import ExpediaClient
    from backend.services.ota.agoda import AgodaClient
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_ERROR = f"Import error: {str(e)}\n{traceback.format_exc()}"
    BookingClient = None
    ExpediaClient = None
    AgodaClient = None


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to fetch reviews."""
        try:
            # Check for import errors first
            if IMPORT_ERROR:
                self._send_error(500, f"Module import failed: {IMPORT_ERROR}")
                return

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            # Extract parameters
            hotel_name = data.get('hotel_name', '')
            sources = data.get('sources', ['booking', 'expedia', 'agoda'])
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
                "reviews": [r.model_dump(mode='json') for r in reviews]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self._send_error(500, f"Internal server error: {str(e)}\\n{error_details}")

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
        if 'booking' in sources:
            clients['booking'] = BookingClient()
        if 'expedia' in sources:
            clients['expedia'] = ExpediaClient()
        if 'agoda' in sources:
            clients['agoda'] = AgodaClient()

        # Calculate reviews per OTA (distribute evenly)
        num_otas = len(clients)
        reviews_per_ota = max_reviews // num_otas if num_otas > 0 else max_reviews

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
                reviews = await client.fetch_reviews(hotel_id, limit=reviews_per_ota)
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
