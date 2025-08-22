"""
Health Check Router
Handles health check and debugging endpoints
Extracted from main.py for better modularity
"""

from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "Tenzai Chatbot API", 
        "timestamp": datetime.now().isoformat()
    }