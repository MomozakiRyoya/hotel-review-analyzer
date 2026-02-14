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

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.excel.generator import ExcelReportGenerator
from backend.models.review import Review
from backend.models.analysis_result import AnalysisResult, OTAAnalysis, SentimentResult


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to export reviews to Excel."""
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

            # Build AnalysisResult
            analysis_result = self._build_analysis_result(reviews, analysis_data)

            # Generate Excel
            generator = ExcelReportGenerator()
            excel_bytes = generator.generate_report(
                reviews=reviews,
                analysis_result=analysis_result,
                hotel_name=hotel_name
            )

            # Convert to base64
            excel_base64 = base64.b64encode(excel_bytes).decode('utf-8')

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "success": True,
                "filename": f"{hotel_name}_reviews_report.xlsx",
                "file_base64": excel_base64,
                "file_size": len(excel_bytes)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        """Handle CORS preflight request."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _build_analysis_result(self, reviews: list, analysis_data: dict) -> AnalysisResult:
        """Build AnalysisResult from data."""
        # Extract keywords
        keywords_data = analysis_data.get('keywords', {})
        all_keywords = keywords_data.get('all', [])
        positive_keywords = keywords_data.get('positive', [])
        negative_keywords = keywords_data.get('negative', [])

        # Extract statistics
        stats = analysis_data.get('statistics', {})
        total_reviews = stats.get('total_reviews', len(reviews))
        avg_rating = stats.get('average_rating', 0)

        # Build OTA analyses (simplified)
        ota_analyses = []
        ota_groups = {}
        for review in reviews:
            if review.source not in ota_groups:
                ota_groups[review.source] = []
            ota_groups[review.source].append(review)

        for source, source_reviews in ota_groups.items():
            ota_analyses.append(OTAAnalysis(
                ota_source=source,
                total_reviews=len(source_reviews),
                average_rating=sum(r.rating for r in source_reviews) / len(source_reviews),
                sentiment_distribution={
                    "positive": len([r for r in source_reviews if r.rating >= 4]),
                    "neutral": len([r for r in source_reviews if r.rating == 3]),
                    "negative": len([r for r in source_reviews if r.rating <= 2])
                },
                top_keywords=all_keywords[:5]
            ))

        return AnalysisResult(
            total_reviews=total_reviews,
            average_rating=avg_rating,
            sentiment_distribution=stats.get('sentiment_distribution', {}),
            top_keywords=all_keywords,
            positive_keywords=positive_keywords,
            negative_keywords=negative_keywords,
            ota_analyses=ota_analyses,
            sentiment_trend=[]  # Not implemented for simplicity
        )

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
