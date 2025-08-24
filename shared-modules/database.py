"""
Shared Database Service - Supabase operations
Independent functions that can be used by both chatbot and order services
Extracted from chatbot-api/services/database_service.py
"""
import uuid
from typing import Dict, Optional
import httpx
from fastapi import HTTPException
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY

async def supabase_request(method: str, endpoint: str, data: Dict = None, use_service_key: bool = True) -> Dict:
    """Make request to Supabase REST API with enhanced error handling"""
    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        # Add Prefer header for POST requests to return created data
        if method == "POST":
            headers["Prefer"] = "return=representation"
        
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        print(f"📡 {method} {endpoint} (service_key: {use_service_key})")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"📊 Response: {response.status_code}")
        
        if response.status_code >= 400:
            error_text = response.text
            print(f"❌ Supabase error: {response.status_code} - {error_text}")
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Database error: {error_text}"
            )
        
        return response.json() if response.text else {}
        
    except httpx.TimeoutException:
        print("⏱️ Supabase request timeout")
        raise HTTPException(status_code=504, detail="Database timeout")
    except httpx.RequestError as e:
        print(f"🔌 Supabase connection error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        print(f"💥 Unexpected database error: {e}")
        raise HTTPException(status_code=500, detail="Internal database error")

async def find_or_create_customer(name: str, phone: str, platform: str = "WEB", platform_user_id: str = None) -> str:
    """Find existing customer or create new one"""
    try:
        # For LINE users, try to find by LINE user ID first
        if platform == "LINE" and platform_user_id:
            print(f"🔍 Looking for LINE user: {platform_user_id}")
            existing_line = await supabase_request("GET", f"customers?line_user_id=eq.{platform_user_id}")
            
            if existing_line:
                existing_customer = existing_line[0]
                print(f"👤 Found existing LINE customer: {existing_customer['id']}")
                
                # Update phone/name if different
                if existing_customer.get('phone') != phone or existing_customer.get('display_name') != name:
                    print(f"📝 Updating customer info: phone={phone}, name={name}")
                    await supabase_request("PATCH", f"customers?id=eq.{existing_customer['id']}", {
                        "phone": phone,
                        "display_name": name
                    })
                
                return existing_customer['id']
        
        # Try to find existing customer by phone
        existing = await supabase_request("GET", f"customers?phone=eq.{phone}")
        
        if existing:
            existing_customer = existing[0]
            print(f"👤 Found existing customer by phone: {existing_customer['id']}")
            
            # Update LINE user ID if provided and different
            if platform == "LINE" and platform_user_id and existing_customer.get('line_user_id') != platform_user_id:
                print(f"📝 Updating LINE user ID: {platform_user_id}")
                try:
                    await supabase_request("PATCH", f"customers?id=eq.{existing_customer['id']}", {
                        "line_user_id": platform_user_id,
                        "platform_type": platform
                    })
                except Exception as e:
                    print(f"⚠️ Could not update LINE user ID (may be duplicate): {e}")
            
            return existing_customer['id']
        
        # Create new customer
        customer_id = str(uuid.uuid4())
        customer_data = {
            "id": customer_id,
            "display_name": name,
            "phone": phone,
            "platform_type": platform,
            "line_user_id": platform_user_id if platform == "LINE" else None
        }
        
        print(f"🆕 Creating new customer: {customer_data}")
        created = await supabase_request("POST", "customers", customer_data)
        print(f"✅ Created new customer: {customer_id}")
        
        return customer_id
        
    except Exception as e:
        print(f"❌ Customer operation error: {e}")
        # Don't return a fake UUID - raise the error
        raise HTTPException(status_code=500, detail=f"Customer creation failed: {str(e)}")

# Database query helpers for common operations
async def get_menu_items() -> list:
    """Get all active menu items"""
    try:
        return await supabase_request("GET", "menu_items?active=eq.true")
    except Exception as e:
        print(f"❌ Error getting menu items: {e}")
        return []

async def get_customer_orders(customer_id: str) -> list:
    """Get orders for a specific customer"""
    try:
        return await supabase_request("GET", f"orders?customer_id=eq.{customer_id}&order=created_at.desc")
    except Exception as e:
        print(f"❌ Error getting customer orders: {e}")
        return []

async def log_conversation(line_user_id: str, message_text: str, response_text: str) -> bool:
    """Log conversation to database"""
    try:
        conversation_data = {
            "line_user_id": line_user_id,
            "message_text": message_text,
            "response_text": response_text
        }
        await supabase_request("POST", "conversations", conversation_data)
        return True
    except Exception as e:
        print(f"⚠️ Failed to log conversation: {e}")
        return False