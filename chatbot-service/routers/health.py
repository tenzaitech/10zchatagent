"""
Health Check Router for Chatbot Service
Simple health monitoring endpoint
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint for chatbot service"""
    return {
        "status": "healthy",
        "service": "chatbot",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }