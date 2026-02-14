"""
Minimal test endpoint for Vercel deployment debugging.
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Test endpoint works!"}

@app.get("/health")
def health():
    return {"status": "healthy", "test": True}

# Export for Vercel with Mangum adapter
handler = Mangum(app)
