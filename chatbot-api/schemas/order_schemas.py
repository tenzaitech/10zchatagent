"""
Order-related Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    """Schema for creating order items"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., ge=1, le=99)
    price: float = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class CustomerInfo(BaseModel):
    """Schema for customer information"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)


class OrderCreate(BaseModel):
    """Schema for creating new orders"""
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=10, max_length=15)
    items: List[OrderItemCreate] = Field(..., min_items=1)
    total_amount: float = Field(..., ge=0)
    order_type: str = Field(..., regex="^(pickup|delivery)$")
    payment_method: Optional[str] = Field("cash", regex="^(cash|card|qr|bank_transfer)$")
    notes: Optional[str] = Field(None, max_length=1000)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: str = Field(..., regex="^(pending|confirmed|preparing|ready|completed|cancelled)$")


class OrderResponse(BaseModel):
    """Schema for order response"""
    order_number: str
    status: str
    customer_name: str
    customer_phone: str
    total_amount: float
    order_type: str
    payment_status: str
    created_at: str
    items: List[Dict[str, Any]]
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Schema for order item in response"""
    name: str
    quantity: int
    unit_price: float
    total_price: float
    notes: Optional[str] = None


class StatusTimelineItem(BaseModel):
    """Schema for order status timeline"""
    status: str
    text: str
    completed: bool


class OrderTrackingResponse(BaseModel):
    """Schema for order tracking response"""
    order_number: str
    status: str
    customer_name: str
    customer_phone: str
    total_amount: float
    payment_status: str
    order_type: str
    created_at: str
    items: List[OrderItemResponse]
    status_history: List[StatusTimelineItem]
    notes: Optional[str] = None