"""
Reviews analyze endpoint for Vercel.
Analyzes hotel reviews with sentiment analysis and keyword extraction.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use lightweight analyzer for Vercel
from backend.services.analyzer.sentiment_lite import SentimentAnalyzerLite
from backend.services.analyzer.keyword import KeywordExtractor
from backend.models.review import Review


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request to analyze reviews."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            # Extract reviews
            reviews_data = data.get('reviews', [])
            if not reviews_data:
                self._send_error(400, "reviews array is required")
                return

            # Convert to Review objects
            reviews = [Review(**r) for r in reviews_data]

            # Initialize analyzers
            sentiment_analyzer = SentimentAnalyzerLite()
            keyword_extractor = KeywordExtractor()

            # Analyze sentiment (modifies reviews in-place)
            reviews = sentiment_analyzer.analyze_reviews(reviews)

            # Build sentiment results
            sentiment_results = []
            for review in reviews:
                sentiment_results.append({
                    "review_id": review.review_id,
                    "sentiment": review.sentiment,
                    "score": review.sentiment_score,
                    "confidence": review.confidence
                })

            # Extract keywords
            keywords_results = keyword_extractor.extract_keywords_from_reviews(reviews, top_n=20)
            keywords = [(k.keyword, k.frequency) for k in keywords_results]

            # Separate positive/negative keywords
            positive_reviews = [r for r in reviews if r.rating >= 4]
            negative_reviews = [r for r in reviews if r.rating <= 2]

            positive_keywords_results = keyword_extractor.extract_keywords_from_reviews(positive_reviews, top_n=10) if positive_reviews else []
            negative_keywords_results = keyword_extractor.extract_keywords_from_reviews(negative_reviews, top_n=10) if negative_reviews else []

            positive_keywords = [(k.keyword, k.frequency) for k in positive_keywords_results]
            negative_keywords = [(k.keyword, k.frequency) for k in negative_keywords_results]

            # Calculate statistics
            total_reviews = len(reviews)
            avg_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0
            avg_sentiment = sum(s["score"] for s in sentiment_results if s["score"] is not None) / total_reviews if total_reviews > 0 else 0

            sentiment_distribution = {
                "positive": len([s for s in sentiment_results if s["sentiment"] == "positive"]),
                "neutral": len([s for s in sentiment_results if s["sentiment"] == "neutral"]),
                "negative": len([s for s in sentiment_results if s["sentiment"] == "negative"])
            }

            # Rating distribution
            rating_distribution = {}
            for review in reviews:
                rating_key = str(int(review.rating))
                rating_distribution[rating_key] = rating_distribution.get(rating_key, 0) + 1

            # Format keywords as expected by frontend
            formatted_keywords = [{"keyword": kw, "frequency": freq, "score": 0, "category": "general"} for kw, freq in keywords]
            formatted_positive = [{"keyword": kw, "frequency": freq} for kw, freq in positive_keywords]
            formatted_negative = [{"keyword": kw, "frequency": freq} for kw, freq in negative_keywords]

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                "success": True,
                "message": f"Successfully analyzed {total_reviews} reviews",
                "analysis_result": {
                    "total_reviews": total_reviews,
                    "average_rating": round(avg_rating, 2),
                    "average_sentiment": round(avg_sentiment, 3),
                    "processing_time": 0,
                    "sentiment_distribution": sentiment_distribution,
                    "rating_distribution": rating_distribution,
                    "top_keywords": formatted_keywords,
                    "positive_keywords": formatted_positive,
                    "negative_keywords": formatted_negative,
                    "ota_analyses": [],
                    "sentiment_trend": []
                }
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
