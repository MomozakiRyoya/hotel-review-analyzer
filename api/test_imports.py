"""
Test endpoint to check what imports are failing.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        results = {
            "python_version": sys.version,
            "path": sys.path[:3],
            "imports": {}
        }

        # Test standard library
        try:
            import datetime
            import random
            import asyncio
            results["imports"]["stdlib"] = "✅ OK"
        except Exception as e:
            results["imports"]["stdlib"] = f"❌ {str(e)}"

        # Test dependencies
        try:
            import httpx
            results["imports"]["httpx"] = "✅ OK"
        except Exception as e:
            results["imports"]["httpx"] = f"❌ {str(e)}"

        try:
            import loguru
            results["imports"]["loguru"] = "✅ OK"
        except Exception as e:
            results["imports"]["loguru"] = f"❌ {str(e)}"

        try:
            import pydantic
            results["imports"]["pydantic"] = "✅ OK"
        except Exception as e:
            results["imports"]["pydantic"] = f"❌ {str(e)}"

        # Test backend modules
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        try:
            from backend.models.review import Review, OTASource
            results["imports"]["backend.models"] = "✅ OK"
        except Exception as e:
            results["imports"]["backend.models"] = f"❌ {str(e)}"

        try:
            from backend.services.ota.api_keys import get_booking_credentials
            results["imports"]["backend.services.ota.api_keys"] = "✅ OK"
        except Exception as e:
            results["imports"]["backend.services.ota.api_keys"] = f"❌ {str(e)}"

        try:
            from backend.services.ota.booking import BookingClient
            results["imports"]["backend.services.ota.booking"] = "✅ OK"
        except Exception as e:
            results["imports"]["backend.services.ota.booking"] = f"❌ {str(e)}"

        try:
            from backend.services.ota.expedia import ExpediaClient
            results["imports"]["backend.services.ota.expedia"] = "✅ OK"
        except Exception as e:
            results["imports"]["backend.services.ota.expedia"] = f"❌ {str(e)}"

        try:
            from backend.services.ota.agoda import AgodaClient
            results["imports"]["backend.services.ota.agoda"] = "✅ OK"
        except Exception as e:
            results["imports"]["backend.services.ota.agoda"] = f"❌ {str(e)}"

        self.wfile.write(json.dumps(results, ensure_ascii=False, indent=2).encode('utf-8'))
