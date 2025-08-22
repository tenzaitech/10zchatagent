"""
Database V2 Service - Dual Write System
Handles both V1 (current) and V2 (enhanced) database operations
Enables zero-downtime migration with instant rollback capability
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pytz import timezone

from services.database_service import supabase_request

class DatabaseV2Service:
    """Database service with dual-write capability for migration"""
    
    def __init__(self):
        self.thailand_tz = timezone('Asia/Bangkok')
        # Migration mode: 'v1_only', 'dual_write', 'v2_only'
        self.migration_mode = 'v1_only'  # Start with V1 only
    
    def set_migration_mode(self, mode: str):
        """Set migration mode for gradual rollout"""
        valid_modes = ['v1_only', 'dual_write', 'v2_only']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of: {valid_modes}")
        self.migration_mode = mode
        print(f"🔄 Database migration mode set to: {mode}")
    
    async def create_customer_v2(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer with V2 enhancements"""
        enhanced_data = {
            **customer_data,
            "platform_type": customer_data.get("platform_type", "WEB"),
            "lifetime_value": 0.00,
            "tags": customer_data.get("tags", []),
            "preferences": customer_data.get("preferences", {}),
            "marketing_consent": customer_data.get("marketing_consent", False),
            "created_at": datetime.now(self.thailand_tz).isoformat(),
            "updated_at": datetime.now(self.thailand_tz).isoformat()
        }
        
        if self.migration_mode == 'v1_only':
            # Write only to V1 format
            return await self._create_customer_v1(customer_data)
        elif self.migration_mode == 'dual_write':
            # Write to both V1 and V2
            result_v1 = await self._create_customer_v1(customer_data)
            try:
                result_v2 = await self._create_customer_v2_enhanced(enhanced_data)
                return result_v1  # Return V1 for compatibility
            except Exception as e:
                print(f"⚠️ V2 customer create failed: {e}")
                return result_v1  # Fallback to V1
        else:  # v2_only
            return await self._create_customer_v2_enhanced(enhanced_data)
    
    async def _create_customer_v1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy customer creation (current system)"""
        return await supabase_request("POST", "customers", data)
    
    async def _create_customer_v2_enhanced(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced customer creation with V2 features"""
        return await supabase_request("POST", "customers", data)
    
    async def create_order_v2(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create order with V2 enhancements"""
        enhanced_data = {
            **order_data,
            "branch_id": order_data.get("branch_id"),
            "delivery_fee": order_data.get("delivery_fee", 0.00),
            "discount_amount": order_data.get("discount_amount", 0.00),
            "tax_amount": order_data.get("tax_amount", 0.00),
            "net_amount": self._calculate_net_amount(order_data),
            "delivery_address": order_data.get("delivery_address"),
            "estimated_ready_at": order_data.get("estimated_ready_at"),
            "metadata": order_data.get("metadata", {}),
            "created_at": datetime.now(self.thailand_tz).isoformat(),
            "updated_at": datetime.now(self.thailand_tz).isoformat()
        }
        
        if self.migration_mode == 'v1_only':
            return await self._create_order_v1(order_data)
        elif self.migration_mode == 'dual_write':
            result_v1 = await self._create_order_v1(order_data)
            try:
                # Create audit trail for V2
                await self._create_order_status_history(result_v1[0], "pending", "Order created")
                result_v2 = await self._create_order_v2_enhanced(enhanced_data)
                return result_v1
            except Exception as e:
                print(f"⚠️ V2 order create failed: {e}")
                return result_v1
        else:  # v2_only
            result = await self._create_order_v2_enhanced(enhanced_data)
            # Create audit trail
            await self._create_order_status_history(result[0], "pending", "Order created")
            return result
    
    async def _create_order_v1(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Legacy order creation"""
        return await supabase_request("POST", "orders", data)
    
    async def _create_order_v2_enhanced(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced order creation with V2 features"""
        return await supabase_request("POST", "orders", data)
    
    async def update_order_status_v2(self, order_number: str, new_status: str, 
                                   staff_id: Optional[str] = None, 
                                   reason: Optional[str] = None) -> Dict[str, Any]:
        """Update order status with V2 audit trail"""
        
        # Get current order first
        orders = await supabase_request("GET", f"orders?order_number=eq.{order_number}&limit=1")
        if not orders:
            raise Exception(f"Order {order_number} not found")
        
        current_order = orders[0]
        old_status = current_order.get("status")
        
        update_data = {
            "status": new_status,
            "updated_at": datetime.now(self.thailand_tz).isoformat()
        }
        
        # Add completion timestamp for completed orders
        if new_status == "completed":
            update_data["completed_at"] = datetime.now(self.thailand_tz).isoformat()
        
        # Add cancellation reason
        if new_status == "cancelled" and reason:
            update_data["cancelled_reason"] = reason
        
        if self.migration_mode == 'v1_only':
            result = await supabase_request("PATCH", f"orders?order_number=eq.{order_number}", update_data)
        elif self.migration_mode == 'dual_write':
            result = await supabase_request("PATCH", f"orders?order_number=eq.{order_number}", update_data)
            try:
                # Create audit trail
                await self._create_order_status_history(
                    current_order, new_status, 
                    f"Status changed from {old_status} to {new_status}",
                    staff_id, reason
                )
                # Log staff action
                if staff_id:
                    await self._log_staff_action(
                        staff_id, "UPDATE", "orders", current_order["id"],
                        f"Changed order {order_number} status to {new_status}",
                        {"old_status": old_status, "new_status": new_status, "reason": reason}
                    )
            except Exception as e:
                print(f"⚠️ V2 audit logging failed: {e}")
        else:  # v2_only
            result = await supabase_request("PATCH", f"orders?order_number=eq.{order_number}", update_data)
            await self._create_order_status_history(
                current_order, new_status,
                f"Status changed from {old_status} to {new_status}",
                staff_id, reason
            )
            if staff_id:
                await self._log_staff_action(
                    staff_id, "UPDATE", "orders", current_order["id"],
                    f"Changed order {order_number} status to {new_status}",
                    {"old_status": old_status, "new_status": new_status, "reason": reason}
                )
        
        return result
    
    async def _create_order_status_history(self, order: Dict[str, Any], new_status: str, 
                                         description: str, staff_id: Optional[str] = None,
                                         notes: Optional[str] = None):
        """Create order status history record"""
        history_data = {
            "order_id": order["id"],
            "old_status": order.get("status"),
            "new_status": new_status,
            "changed_by": staff_id or "system",
            "description": description,
            "notes": notes,
            "created_at": datetime.now(self.thailand_tz).isoformat()
        }
        
        try:
            await supabase_request("POST", "order_status_history", history_data)
        except Exception as e:
            print(f"⚠️ Failed to create status history: {e}")
    
    async def _log_staff_action(self, staff_id: str, action_type: str, target_type: str,
                               target_id: str, description: str, metadata: Dict[str, Any]):
        """Log staff action for security audit"""
        action_data = {
            "staff_id": staff_id,
            "action_type": action_type,
            "target_type": target_type,
            "target_id": target_id,
            "description": description,
            "metadata": metadata,
            "ip_address": None,  # Would be filled from request context
            "user_agent": None,  # Would be filled from request context
            "created_at": datetime.now(self.thailand_tz).isoformat()
        }
        
        try:
            await supabase_request("POST", "staff_actions", action_data)
        except Exception as e:
            print(f"⚠️ Failed to log staff action: {e}")
    
    def _calculate_net_amount(self, order_data: Dict[str, Any]) -> float:
        """Calculate net amount for order"""
        total = float(order_data.get("total_amount", 0))
        delivery_fee = float(order_data.get("delivery_fee", 0))
        discount = float(order_data.get("discount_amount", 0))
        tax = float(order_data.get("tax_amount", 0))
        
        return total + delivery_fee - discount + tax
    
    async def create_payment_transaction(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment transaction (V2 feature)"""
        if self.migration_mode == 'v1_only':
            # V1 doesn't support payment transactions
            print("⚠️ Payment transactions not supported in V1 mode")
            return {}
        
        enhanced_data = {
            **payment_data,
            "transaction_ref": payment_data.get("transaction_ref", str(uuid.uuid4())),
            "status": payment_data.get("status", "pending"),
            "created_at": datetime.now(self.thailand_tz).isoformat(),
            "updated_at": datetime.now(self.thailand_tz).isoformat()
        }
        
        return await supabase_request("POST", "payment_transactions", enhanced_data)
    
    async def get_order_with_history(self, order_number: str) -> Dict[str, Any]:
        """Get order with status history (V2 feature)"""
        if self.migration_mode == 'v1_only':
            # Fallback to V1 without history
            orders = await supabase_request("GET", f"orders?order_number=eq.{order_number}&limit=1")
            if orders:
                return orders[0]
            return {}
        
        # Get order with full history
        order_query = f"orders?order_number=eq.{order_number}&select=*,order_items(*),order_status_history(*)&limit=1"
        orders = await supabase_request("GET", order_query, use_service_key=False)
        
        if orders:
            return orders[0]
        return {}

# Global instance
db_v2 = DatabaseV2Service()