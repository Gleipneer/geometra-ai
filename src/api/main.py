"""Main FastAPI application for Geometra AI system."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
from .health import router as health_router
from pydantic import BaseModel

app = FastAPI(
    title="Geometra AI API",
    description="API for Geometra AI system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["system"])

class AIRequest(BaseModel):
    text: str
    type: Optional[str] = "general"

@app.post("/api/ai")
async def ai_endpoint(request: AIRequest):
    try:
        # Här kan vi lägga till mer avancerad AI-logik senare
        response = {
            "status": "success",
            "input": request.text,
            "type": request.type,
            "message": "AI analysis completed"
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/version")
async def get_version() -> Dict[str, str]:
    """Get API version."""
    return {"version": "1.0.0"} 