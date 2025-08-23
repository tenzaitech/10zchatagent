#!/usr/bin/env python3
"""
Tenzai Chatbot API v2.1 - Modular Structure
Main application with extracted routers for better maintainability
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import configuration and validation
from modules.config import validate_config, SUPABASE_URL, LINE_CHANNEL_SECRET

# Import modular routers
from routers import orders, webhooks, admin, health, static

# Load environment variables
load_dotenv()
print("🔧 Loading .env file...")

# Validate configuration
if not validate_config():
    print("❌ Configuration validation failed!")
    exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Tenzai Chatbot API v2.1", 
    version="2.1.0",
    description="Modular restaurant chatbot API with order management"
)

# CORS for web app (including ngrok domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(static.router)
app.include_router(orders.router)
app.include_router(webhooks.router)
app.include_router(admin.router)

print("🚀 Tenzai Chatbot API v2.1 initialized with modular structure!")
print(f"📊 Routers loaded: health, static, orders, webhooks, admin")

# Server startup
if __name__ == "__main__":
    print("🚀 Starting Tenzai Chatbot API v2.1...")
    print(f"🌐 Supabase: {SUPABASE_URL}")
    print(f"🔗 LINE Channel Secret: {'✅' if LINE_CHANNEL_SECRET else '❌'}")
    
    # Run on standard port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)