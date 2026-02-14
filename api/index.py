"""
Welcome page for Hotel Review Analyzer API.
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request to root path."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "message": "Welcome to Hotel Review Analyzer API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "reviews_fetch": "/api/reviews_fetch (POST)",
                "reviews_analyze": "/api/reviews_analyze (POST)",
                "reviews_export": "/api/reviews_export (POST)"
            },
            "documentation": "https://github.com/your-repo/hotel-review-analyzer",
            "status": "operational"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
        return
