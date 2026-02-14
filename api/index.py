"""
Vercel serverless function entry point.
"""
from backend.main import app

# Export the FastAPI app for Vercel
handler = app
