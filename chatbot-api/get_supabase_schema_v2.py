#!/usr/bin/env python3
"""
🔍 Supabase Schema Inspector V2
ดึงข้อมูล database schema โดยตรงจาก Supabase REST API
ใช้สำหรับตรวจสอบโครงสร้าง tables, columns, types

Usage:
    python get_supabase_schema_v2.py
    python get_supabase_schema_v2.py --json schema.json
"""

import os
import sys
import requests
import json
from typing import Dict, List, Any
from datetime import datetime

class SupabaseSchemaInspector:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.url or not self.key:
            # Try reading from privatekey.md
            try:
                with open('../privatekey.md', 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'SUPABASE_URL=' in line:
                            self.url = line.split('=', 1)[1].strip()
                        elif 'SUPABASE_SERVICE_ROLE_KEY=' in line:
                            self.key = line.split('=', 1)[1].strip()
            except:
                pass
                
        if not self.url or not self.key:
            print("❌ Error: ไม่พบ SUPABASE_URL และ SUPABASE_SERVICE_ROLE_KEY")
            print("   ตั้งใน environment หรือใส่ไว้ใน privatekey.md")
            sys.exit(1)
            
        self.base_url = f"{self.url}/rest/v1"
        self.openapi_url = f"{self.url}/rest/v1/"
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
        
    def get_schema_definition(self):
        """ดึง OpenAPI schema definition จาก Supabase"""
        try:
            response = requests.get(self.openapi_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting schema: {e}")
            return None
            
    def extract_table_info(self, schema_data):
        """แยกข้อมูล tables จาก schema definition"""
        tables = {}
        definitions = schema_data.get('definitions', {})
        
        for name, props in definitions.items():
            if props.get('type') == 'object' and 'properties' in props:
                columns = list(props['properties'].keys())
                tables[name] = {
                    'columns': columns,
                    'column_count': len(columns),
                    'properties': props['properties']
                }
                
        return tables
        
    def get_table_row_count(self, table_name: str) -> int:
        """ดึงจำนวน rows ใน table"""
        try:
            response = requests.get(
                f"{self.base_url}/{table_name}?limit=1",
                headers={**self.headers, 'Prefer': 'count=exact'}
            )
            
            if response.status_code == 200:
                content_range = response.headers.get('content-range', '0-0/0')
                total = content_range.split('/')[-1]
                return int(total) if total != '*' else -1
            else:
                return -1
        except:
            return -1
            
    def format_column_details(self, properties: Dict) -> List[str]:
        """จัดรูปแบบรายละเอียด columns"""
        column_info = []
        for col_name, col_props in properties.items():
            col_type = col_props.get('type', 'unknown')
            if col_type == 'string':
                format_info = col_props.get('format', '')
                if format_info:
                    col_type = f"string({format_info})"
            elif col_type == 'integer':
                format_info = col_props.get('format', '')
                if format_info == 'int64':
                    col_type = 'bigint'
                    
            description = col_props.get('description', '')
            
            column_info.append(f"    {col_name:<25} {col_type:<15} {description}")
            
        return column_info
        
    def inspect_schema(self):
        """ตรวจสอบ schema ทั้งหมด"""
        print("🔍 SUPABASE SCHEMA INSPECTOR V2")
        print("=" * 65)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL: {self.url}")
        print("=" * 65)
        
        # ดึง schema definition
        schema_data = self.get_schema_definition()
        if not schema_data:
            print("❌ ไม่สามารถดึง schema definition ได้")
            return
            
        # แยกข้อมูล tables
        tables = self.extract_table_info(schema_data)
        
        if not tables:
            print("❌ ไม่พบ tables ใน schema")
            return
            
        print(f"📋 พบ {len(tables)} tables:")
        
        # แสดงข้อมูลแต่ละ table
        for table_name in sorted(tables.keys()):
            table_info = tables[table_name]
            print(f"\n📋 TABLE: {table_name.upper()}")
            print("-" * 50)
            
            # Row count
            row_count = self.get_table_row_count(table_name)
            count_display = f"{row_count:,}" if row_count >= 0 else "[Access Denied]"
            print(f"📊 Records: {count_display}")
            print(f"🏗️  Columns: {table_info['column_count']}")
            
            # Column details
            print("📝 Column Details:")
            column_details = self.format_column_details(table_info['properties'])
            for detail in column_details:
                print(detail)
                
        print("\n" + "=" * 65)
        print("✅ Schema inspection completed!")
        
    def export_to_json(self, filename: str = "supabase_schema.json"):
        """Export schema เป็น JSON file"""
        schema_data = self.get_schema_definition()
        if not schema_data:
            print("❌ ไม่สามารถดึง schema ได้")
            return
            
        tables = self.extract_table_info(schema_data)
        
        # เพิ่มข้อมูล row count
        for table_name in tables.keys():
            tables[table_name]['row_count'] = self.get_table_row_count(table_name)
            
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "supabase_url": self.url,
            "table_count": len(tables),
            "tables": tables
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            
        print(f"💾 Schema exported to {filename}")
        
    def create_performance_indexes(self):
        """สร้าง SQL script สำหรับ performance indexes"""
        sql_script = """-- 🚀 PERFORMANCE INDEXES FOR SUPABASE
-- สร้าง indexes เพื่อเพิ่มความเร็วในการ query

-- Orders table (หลัก)
CREATE INDEX IF NOT EXISTS idx_orders_status 
ON orders(status);

CREATE INDEX IF NOT EXISTS idx_orders_created_date 
ON orders(created_at::date);

CREATE INDEX IF NOT EXISTS idx_orders_customer 
ON orders(customer_id);

-- Partial indexes สำหรับ active orders
CREATE INDEX IF NOT EXISTS idx_orders_pending 
ON orders(status) 
WHERE status IN ('pending','confirmed','preparing');

CREATE INDEX IF NOT EXISTS idx_orders_today 
ON orders(created_at) 
WHERE created_at::date = CURRENT_DATE;

-- Payment transactions
CREATE INDEX IF NOT EXISTS idx_payments_order 
ON payment_transactions(order_id);

CREATE INDEX IF NOT EXISTS idx_payments_status 
ON payment_transactions(status);

-- Customers
CREATE INDEX IF NOT EXISTS idx_customers_platform 
ON customers(line_user_id);

CREATE INDEX IF NOT EXISTS idx_customers_phone 
ON customers(phone);

-- Order Status History (สำหรับ audit trail)
CREATE INDEX IF NOT EXISTS idx_order_history_order 
ON order_status_history(order_id);

CREATE INDEX IF NOT EXISTS idx_order_history_created 
ON order_status_history(created_at);

-- Staff Actions (สำหรับ security audit)
CREATE INDEX IF NOT EXISTS idx_staff_actions_created 
ON staff_actions(created_at);

-- Order Items
CREATE INDEX IF NOT EXISTS idx_order_items_order 
ON order_items(order_id);

ANALYZE; -- Update statistics

-- 📊 คาดการณ์ผลลัพธ์:
-- • Query orders by status: 500ms → 50ms (10x เร็วขึ้น)
-- • Load today's orders: 300ms → 30ms (10x เร็วขึ้น)  
-- • Customer lookup: 200ms → 20ms (10x เร็วขึ้น)
-- • Payment verification: 400ms → 40ms (10x เร็วขึ้น)
"""
        
        with open('performance_indexes.sql', 'w', encoding='utf-8') as f:
            f.write(sql_script)
            
        print("📈 Performance indexes SQL สร้างแล้ว: performance_indexes.sql")
        print("   รัน script นี้ใน Supabase SQL Editor เพื่อเพิ่ม performance")


def main():
    inspector = SupabaseSchemaInspector()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--json':
            # Export เป็น JSON
            filename = sys.argv[2] if len(sys.argv) > 2 else "supabase_schema.json"
            inspector.export_to_json(filename)
        elif sys.argv[1] == '--indexes':
            # สร้าง performance indexes SQL
            inspector.create_performance_indexes()
        else:
            print("Usage: python get_supabase_schema_v2.py [--json filename] [--indexes]")
    else:
        # แสดงผลใน console
        inspector.inspect_schema()


if __name__ == "__main__":
    main()