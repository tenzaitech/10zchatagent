"""
Admin Router
Handles admin dashboard endpoints and staff notifications
Extracted from main.py for better modularity
"""

from datetime import datetime
from fastapi import APIRouter, Request, HTTPException

from services.database_service import supabase_request

router = APIRouter(prefix="/api", tags=["admin"])

@router.get("/schema/inspect")
async def inspect_database_schema():
    """Get basic table information from Supabase (simplified version)"""
    try:
        # Since we can't use SQL directly, get table info from sample data
        tables = ['customers', 'orders', 'order_items', 'menus', 'categories', 'conversations']
        schemas = {}
        
        for table_name in tables:
            try:
                print(f"📋 Inspecting table: {table_name}")
                # Get sample data to see column structure
                data = await supabase_request("GET", f"{table_name}?limit=1", use_service_key=False)
                
                if data and len(data) > 0:
                    columns = list(data[0].keys())
                    schemas[table_name] = {
                        "columns": columns,
                        "sample_count": len(data),
                        "accessible": True
                    }
                else:
                    schemas[table_name] = {
                        "columns": [],
                        "sample_count": 0,
                        "accessible": True,
                        "note": "Empty table"
                    }
                    
            except Exception as e:
                print(f"❌ Error inspecting {table_name}: {e}")
                schemas[table_name] = {
                    "error": str(e),
                    "accessible": False
                }
        
        return {
            "status": "success",
            "schemas": schemas,
            "timestamp": datetime.now().isoformat(),
            "note": "Simplified schema inspection (no SQL execution)"
        }
        
    except Exception as e:
        print(f"❌ Schema inspection error: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/schema/sample-data")
async def get_sample_data():
    """Get sample data from all tables to see structure"""
    try:
        samples = {}
        tables = ['customers', 'orders', 'order_items', 'menus', 'categories', 'conversations']
        
        for table in tables:
            try:
                print(f"📊 Getting sample from {table}...")
                # Get first row to see structure
                data = await supabase_request("GET", f"{table}?limit=1", use_service_key=False)
                samples[table] = {
                    'sample_row': data[0] if data else None,
                    'columns': list(data[0].keys()) if data else [],
                    'row_count': len(data)
                }
            except Exception as e:
                print(f"❌ Error accessing {table}: {e}")
                samples[table] = {
                    'error': str(e),
                    'accessible': False
                }
        
        return {
            "status": "success",
            "samples": samples,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Sample data error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/staff/notifications")
async def create_staff_notification(request: Request):
    """Create staff notification record"""
    try:
        data = await request.json()
        
        notification_data = {
            "order_number": data.get("order_number"),
            "notification_type": data.get("notification_type", "new_order"),
            "message": data.get("message", ""),
            "sent_at": datetime.now().isoformat(),
            "status": data.get("status", "sent")
        }
        
        result = await supabase_request("POST", "staff_notifications", notification_data)
        
        return {
            "success": True,
            "message": "Staff notification logged"
        }
        
    except Exception as e:
        print(f"❌ Error creating staff notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create staff notification")