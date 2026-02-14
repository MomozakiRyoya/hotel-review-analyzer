"""
Minimal test endpoint for Vercel deployment debugging.
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Test endpoint works!"}

@app.get("/health")
def health():
    return {"status": "healthy", "test": True}

# Export for Vercel
handler = app
