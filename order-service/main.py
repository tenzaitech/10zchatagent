#!/usr/bin/env python3
"""
Tenzai Order Service - Dedicated Order Management
Handles order CRUD, payments, admin functions, and static file serving
Separated from chatbot for better scalability and maintainability
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

# Import order-specific routers
from routers.orders import router as orders_router
from routers.admin import router as admin_router
from routers.static import router as static_router
from routers.health import router as health_router
from routers.notifications import router as notifications_router

# Load environment variables
load_dotenv("../.env")  # Load from parent directory
print("🛒 Loading Order Service...")

# Validate configuration
if not validate_config():
    print("❌ Configuration validation failed!")
    exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Tenzai Order Service", 
    version="1.0.0",
    description="Order management and payment processing service"
)

# CORS for web app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include order-specific routers
app.include_router(health_router)
app.include_router(static_router)
app.include_router(orders_router)
app.include_router(admin_router)
app.include_router(notifications_router)

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "service": "Tenzai Order Service",
        "version": "1.0.0",
        "status": "running",
        "description": "Order management and payment processing",
        "endpoints": {
            "/api/orders": "Order CRUD operations",
            "/api/admin": "Admin dashboard functions",
            "/api/notifications": "Order status notifications",
            "/health": "Service health check",
            "/": "Customer webapp"
        }
    }

if __name__ == "__main__":
    # Run order service on port 8002
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)