"""
Reviews export endpoint for Vercel.
Exports analyzed reviews to Excel format.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
import base64
import io
import csv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models.review import Review

# Excel dependencies not available in minimal deployment
EXCEL_AVAILABLE = False
try:
    from backend.services.excel.generator import ExcelReportGenerator
    from backend.models.analysis_result import AnalysisResult, OTAAnalysis, SentimentResult
    EXCEL_AVAILABLE = True
except ImportError:
    pass


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to export reviews."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            # Extract data
            reviews_data = data.get('reviews', [])
            analysis_data = data.get('analysis', {})
            hotel_name = data.get('hotel_name', 'Hotel')

            if not reviews_data:
                self._send_error(400, "reviews array is required")
                return

            # Convert to Review objects
            reviews = [Review(**r) for r in reviews_data]

            # Generate CSV instead of Excel (lightweight)
            csv_bytes = self._generate_csv(reviews, hotel_name)

            # Convert to base64
            csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "success": True,
                "message": "CSV export generated (Excel unavailable in serverless)",
                "filename": f"{hotel_name}_reviews_export.csv",
                "file_base64": csv_base64,
                "file_size": len(csv_bytes),
                "format": "csv"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            import traceback
            self._send_error(500, f"Internal server error: {str(e)}\n{traceback.format_exc()}")

    def do_OPTIONS(self):
        """Handle CORS preflight request."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


    def _generate_csv(self, reviews: list, hotel_name: str) -> bytes:
        """Generate CSV export of reviews."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Review ID', 'Hotel Name', 'OTA Source', 'Rating',
            'Review Date', 'Comment', 'Reviewer Name', 'Trip Type'
        ])

        # Write reviews
        for review in reviews:
            writer.writerow([
                review.review_id,
                review.hotel_name,
                review.source.value if hasattr(review.source, 'value') else review.source,
                review.rating,
                review.review_date.strftime('%Y-%m-%d') if review.review_date else '',
                review.comment[:200],  # Truncate long comments
                review.reviewer_name or '',
                review.trip_type or ''
            ])

        return output.getvalue().encode('utf-8')

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
