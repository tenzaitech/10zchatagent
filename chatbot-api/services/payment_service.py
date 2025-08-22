"""
Payment Service - QR Code Generation and Verification
Handles PromptPay QR generation, slip verification, and payment processing
Part of Database V2 Payment System
"""

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    print("⚠️ qrcode library not available - QR generation disabled")
    QR_AVAILABLE = False

import uuid
import base64
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pytz import timezone

from services.database_v2 import db_v2


class PaymentService:
    """Payment processing service with QR generation and verification"""
    
    def __init__(self):
        self.thailand_tz = timezone('Asia/Bangkok')
        self.promptpay_id = "0123456789"  # PromptPay phone number (to be configured)
    
    def generate_promptpay_qr(self, amount: float, order_number: str) -> Dict[str, Any]:
        """Generate PromptPay QR code for payment"""
        try:
            # Create QR payload using PromptPay format
            # Simplified version - real implementation would use proper PromptPay format
            qr_payload = self._create_promptpay_payload(self.promptpay_id, amount, order_number)
            
            # Generate unique transaction reference
            transaction_ref = f"TXN_{order_number}_{uuid.uuid4().hex[:8].upper()}"
            
            qr_data = {
                "qr_payload": qr_payload,
                "transaction_ref": transaction_ref,
                "amount": amount,
                "valid_until": (datetime.now(self.thailand_tz) + timedelta(hours=1)).isoformat(),
                "promptpay_id": self.promptpay_id
            }
            
            if QR_AVAILABLE:
                # Generate QR code image
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_payload)
                qr.make(fit=True)
                
                # Create QR image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64 for API response
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                qr_data["qr_image_base64"] = f"data:image/png;base64,{img_base64}"
            else:
                qr_data["qr_image_base64"] = "data:text/plain;base64,UVIgZ2VuZXJhdGlvbiBub3QgYXZhaWxhYmxl"  # "QR generation not available"
            
            print(f"✅ Generated PromptPay QR for ฿{amount} - Order {order_number}")
            return qr_data
            
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
            raise Exception(f"Failed to generate QR code: {e}")
    
    def _create_promptpay_payload(self, promptpay_id: str, amount: float, ref: str) -> str:
        """Create PromptPay QR payload (simplified version)"""
        # This is a simplified version. Real PromptPay QR uses EMV QR Code format
        # Format: promptpay_id|amount|reference
        return f"promptpay://{promptpay_id}/{amount:.2f}/{ref}"
    
    async def create_payment_transaction(self, order_id: str, amount: float, 
                                       method: str = "promptpay") -> Dict[str, Any]:
        """Create payment transaction record"""
        try:
            # Generate QR if PromptPay
            qr_data = {}
            if method == "promptpay":
                # Get order number for QR generation
                orders = await db_v2.supabase_request("GET", f"orders?id=eq.{order_id}&select=order_number")
                if not orders:
                    raise Exception("Order not found")
                
                order_number = orders[0]["order_number"]
                qr_data = self.generate_promptpay_qr(amount, order_number)
            
            # Create payment transaction
            payment_data = {
                "order_id": order_id,
                "transaction_ref": qr_data.get("transaction_ref", str(uuid.uuid4())),
                "amount": amount,
                "method": method,
                "status": "pending",
                "qr_payload": qr_data.get("qr_payload"),
                "qr_image_url": None,  # Would store in cloud storage in production
                "valid_until": qr_data.get("valid_until"),
                "created_at": datetime.now(self.thailand_tz).isoformat()
            }
            
            result = await db_v2.create_payment_transaction(payment_data)
            
            # Return transaction with QR data
            transaction_data = result[0] if result else {}
            return {
                **transaction_data,
                "qr_image_base64": qr_data.get("qr_image_base64"),
                "promptpay_id": qr_data.get("promptpay_id")
            }
            
        except Exception as e:
            print(f"❌ Error creating payment transaction: {e}")
            raise Exception(f"Failed to create payment transaction: {e}")
    
    async def verify_payment_slip(self, transaction_id: str, slip_image_data: str) -> Dict[str, Any]:
        """Verify payment slip upload (placeholder for OCR integration)"""
        try:
            # This would integrate with actual slip verification service
            # For now, simulate verification
            
            verification_result = {
                "verified": True,  # Would be actual OCR result
                "amount_detected": 0.0,
                "bank_detected": "Unknown",
                "timestamp_detected": None,
                "confidence_score": 0.85
            }
            
            # Update payment transaction
            update_data = {
                "slip_url": "placeholder_slip_url",  # Would be cloud storage URL
                "slip_uploaded_at": datetime.now(self.thailand_tz).isoformat(),
                "verification_result": verification_result,
                "status": "verifying"
            }
            
            await db_v2.supabase_request("PATCH", f"payment_transactions?id=eq.{transaction_id}", update_data)
            
            print(f"✅ Payment slip uploaded for transaction {transaction_id}")
            return verification_result
            
        except Exception as e:
            print(f"❌ Error verifying payment slip: {e}")
            raise Exception(f"Failed to verify payment slip: {e}")
    
    async def confirm_payment(self, transaction_id: str, verified_by: str = "system") -> Dict[str, Any]:
        """Confirm payment and update order status"""
        try:
            # Get transaction
            transactions = await db_v2.supabase_request("GET", f"payment_transactions?id=eq.{transaction_id}&select=*,orders(order_number)")
            if not transactions:
                raise Exception("Transaction not found")
            
            transaction = transactions[0]
            order_number = transaction["orders"]["order_number"]
            
            # Update transaction status
            update_data = {
                "status": "success",
                "verified_at": datetime.now(self.thailand_tz).isoformat(),
                "verified_by": verified_by
            }
            await db_v2.supabase_request("PATCH", f"payment_transactions?id=eq.{transaction_id}", update_data)
            
            # Update order payment status
            order_update = {
                "payment_status": "paid",
                "status": "confirmed"  # Auto-confirm when payment received
            }
            await db_v2.supabase_request("PATCH", f"orders?order_number=eq.{order_number}", order_update)
            
            print(f"✅ Payment confirmed for order {order_number}")
            return {
                "success": True,
                "order_number": order_number,
                "transaction_id": transaction_id,
                "amount": transaction["amount"],
                "verified_at": update_data["verified_at"]
            }
            
        except Exception as e:
            print(f"❌ Error confirming payment: {e}")
            raise Exception(f"Failed to confirm payment: {e}")
    
    async def get_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Get payment status for an order"""
        try:
            query = f"payment_transactions?order_id=eq.{order_id}&select=*&order=created_at.desc&limit=1"
            transactions = await db_v2.supabase_request("GET", query)
            
            if not transactions:
                return {
                    "status": "no_payment",
                    "message": "No payment transaction found"
                }
            
            transaction = transactions[0]
            return {
                "status": transaction["status"],
                "method": transaction["method"],
                "amount": transaction["amount"],
                "transaction_ref": transaction["transaction_ref"],
                "created_at": transaction["created_at"],
                "verified_at": transaction.get("verified_at")
            }
            
        except Exception as e:
            print(f"❌ Error getting payment status: {e}")
            return {
                "status": "error",
                "message": f"Failed to get payment status: {e}"
            }

# Global instance
payment_service = PaymentService()