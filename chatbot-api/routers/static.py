"""
Static Files Router
Handles HTML pages and static file serving
Extracted from main.py for better modularity
"""

import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["static"])

# Get static files directory
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "webappadmin")

@router.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "customer_webapp.html"))

@router.get("/customer_webapp.html")
async def customer_webapp():
    return FileResponse(os.path.join(static_dir, "customer_webapp.html"))

@router.get("/order-status.html") 
async def order_status():
    return FileResponse(os.path.join(static_dir, "order-status.html"))

@router.get("/favicon.ico")
async def favicon():
    favicon_path = os.path.join(static_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"status": "no favicon"}

@router.get("/admin/edit-menu")
async def admin_menu():
    return FileResponse(os.path.join(static_dir, "edit_menu_dashboard-admin.html"))

@router.get("/admin/staff-orders.html")
async def staff_orders():
    return FileResponse(os.path.join(static_dir, "admin", "staff-orders.html"))