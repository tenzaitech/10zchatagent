#!/usr/bin/env python3
"""
Tenzai Chatbot Service - Dedicated AI Chat Handling
Handles LINE/Facebook webhooks and AI responses only
Separated from order management for better scalability
"""

import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add shared modules to path
shared_path = os.path.join(os.path.dirname(__file__), "..", "shared-modules")
sys.path.insert(0, shared_path)

# Import shared configuration
from config import validate_config

# Import chatbot-specific routers
from routers.webhooks import router as webhook_router
from routers.health import router as health_router

# Load environment variables
load_dotenv("../.env")  # Load from parent directory
print("🤖 Loading Chatbot Service...")

# Validate configuration
if not validate_config():
    print("❌ Configuration validation failed!")
    exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Tenzai Chatbot Service", 
    version="1.0.0",
    description="AI-powered chatbot service for customer support"
)

# CORS for cross-service communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include chatbot-specific routers
app.include_router(health_router)
app.include_router(webhook_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Tenzai Chatbot Service",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered customer support chatbot"
    }

if __name__ == "__main__":
    # Run chatbot service on port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)