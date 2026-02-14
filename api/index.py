"""
Vercel serverless function entry point.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.main import app

# Export the FastAPI app for Vercel
handler = app
