"""
Database service - Supabase operations
Independent functions that can be tested separately
"""
import uuid
from typing import Dict, Optional
import httpx
from fastapi import HTTPException
from modules.config import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY

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
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code not in [200, 201, 204]:
            print(f"❌ Supabase error: {response.status_code}")
            print(f"   URL: {url}")
            print(f"   Headers: {headers}")
            print(f"   Data sent: {data}")
            print(f"   Response: {response.text}")
            raise HTTPException(status_code=500, detail=f"Database error: {response.status_code} - {response.text}")
        
        # Handle response body - Supabase may return empty body with 201 status
        if response.text:
            result = response.json()
            print(f"✅ Supabase response: {len(str(result))} chars")
        else:
            result = []
            print(f"✅ Supabase response: Empty body (Status {response.status_code})")
        
        return result
        
    except httpx.TimeoutException:
        print("❌ Supabase timeout")
        raise HTTPException(status_code=504, detail="Database timeout")
    except httpx.RequestError as e:
        print(f"❌ Supabase connection error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        print(f"❌ Unexpected error in supabase_request: {e}")
        raise HTTPException(status_code=500, detail="Database error")

def generate_platform_id(platform: str, identifier: str = None) -> str:
    """Generate platform-specific customer ID"""
    if platform == "LINE" and identifier:
        return f"LINE_{identifier}"
    elif platform == "FB" and identifier:
        return f"FB_{identifier}"
    elif platform == "IG" and identifier:
        return f"IG_{identifier}"
    elif platform == "WEB":
        # For web orders, use phone number as unique identifier
        if identifier:
            return f"WEB_{identifier}"
        else:
            return f"WEB_{str(uuid.uuid4())[:8]}"
    else:
        return f"UNKNOWN_{str(uuid.uuid4())[:8]}"

async def find_or_create_customer(name: str, phone: str, platform: str = "WEB", platform_user_id: str = None) -> str:
    """Smart customer management - find existing or create new with proper platform ID"""
    try:
        print(f"🔍 Processing customer: name={name}, phone={phone}, platform={platform}")
        platform_id = generate_platform_id(platform, platform_user_id or phone)
        
        # Step 1: For LINE/FB/IG, try to find by platform_user_id first (more reliable)
        if platform != "WEB" and platform_user_id:
            platform_query = f"customers?line_user_id=eq.{platform_id}&select=id,line_user_id,phone&limit=1"
            platform_customers = await supabase_request("GET", platform_query, use_service_key=False)
            
            if platform_customers and len(platform_customers) > 0:
                customer_id = platform_customers[0]["id"]
                existing_phone = platform_customers[0]["phone"]
                
                # Update phone if it has changed
                if existing_phone != phone:
                    update_data = {"phone": phone, "display_name": name}
                    await supabase_request("PATCH", f"customers?id=eq.{customer_id}", update_data)
                    print(f"✅ Updated customer {customer_id} phone: {existing_phone} → {phone}")
                else:
                    print(f"✅ Found existing customer by platform ID: {customer_id}")
                return customer_id
        
        # Step 2: Try to find existing customer by phone (universal key)
        phone_query = f"customers?phone=eq.{phone}&select=id,line_user_id&limit=1"
        phone_customers = await supabase_request("GET", phone_query, use_service_key=False)
        
        if phone_customers and len(phone_customers) > 0:
            customer_id = phone_customers[0]["id"]
            current_platform_id = phone_customers[0]["line_user_id"]
            
            # Update platform ID if it's generic web ID and we have better info
            if current_platform_id.startswith("WEB_") and len(current_platform_id) < 15 and platform != "WEB":
                update_data = {"line_user_id": platform_id, "display_name": name}
                await supabase_request("PATCH", f"customers?id=eq.{customer_id}", update_data)
                print(f"✅ Updated customer {customer_id} platform ID: {current_platform_id} → {platform_id}")
            else:
                print(f"✅ Found existing customer by phone: {customer_id} ({current_platform_id})")
            return customer_id
        
        # Step 3: Create new customer with proper platform ID (V2 schema)
        customer_data = {
            "display_name": name,
            "phone": phone,
            "line_user_id": platform_id,  # Keep for backward compatibility
            "platform_type": platform,  # V2 field
            "merged_from": [],  # V2 field
            "lifetime_value": 0.00,  # V2 field
            "tags": [],  # V2 field
            "metadata": {},  # V2 field
            "total_orders": 0,  # Default value
            "total_spent": 0.00  # Default value
        }
        
        print(f"📝 Creating new customer: {customer_data}")
        customer_result = await supabase_request("POST", "customers", customer_data)
        
        # Handle Supabase response patterns
        if not customer_result or len(customer_result) == 0:
            print("🔄 Customer created but no ID returned, fetching...")
            fetch_query = f"customers?line_user_id=eq.{platform_id}&select=id&limit=1"
            fetch_result = await supabase_request("GET", fetch_query, use_service_key=False)
            if fetch_result and len(fetch_result) > 0:
                customer_id = fetch_result[0]["id"]
                print(f"✅ Fetched new customer ID: {customer_id}")
                return customer_id
        else:
            customer_id = customer_result[0]["id"]
            print(f"✅ Customer created with ID: {customer_id}")
            return customer_id
            
        raise Exception("Failed to create or retrieve customer")
        
    except Exception as e:
        print(f"❌ Customer operation error: {e}")
        raise HTTPException(status_code=500, detail=f"Customer operation failed: {str(e)}")