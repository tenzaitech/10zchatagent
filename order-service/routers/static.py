"""
Static Files Router
Handles HTML pages and static file serving
Extracted from main.py for better modularity
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["static"])

# Get static files directory - use absolute path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go up to 10zchatbot/
static_dir = os.path.join(project_root, "webappadmin")

@router.get("/")
async def root():
    file_path = os.path.join(static_dir, "customer_webapp.html")
    print(f"📄 Project root: {os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}")
    print(f"📄 Static dir: {static_dir}")
    print(f"📄 File path: {file_path}")
    print(f"📄 File exists: {os.path.exists(file_path)}")
    
    # List webappadmin directory contents for debugging
    if os.path.exists(static_dir):
        files = os.listdir(static_dir)
        print(f"📂 Files in webappadmin: {files}")
    else:
        print(f"❌ Static dir does not exist: {static_dir}")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    return FileResponse(file_path)

@router.get("/customer_webapp.html")
async def customer_webapp():
    file_path = os.path.join(static_dir, "customer_webapp.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    return FileResponse(file_path)

@router.get("/order")
async def order_page():
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

@router.get("/staff")
async def staff_dashboard():
    return FileResponse(os.path.join(static_dir, "admin", "staff-orders.html"))

@router.get("/admin")
async def admin_dashboard():
    return FileResponse(os.path.join(static_dir, "admin", "staff-orders.html"))