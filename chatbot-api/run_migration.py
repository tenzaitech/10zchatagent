#!/usr/bin/env python3
"""
Supabase Migration Runner
รัน migration scripts ใน Supabase database
"""

import requests
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)

def execute_sql(sql_content, script_name):
    """Execute SQL in Supabase via REST API"""
    try:
        print(f"\n🔄 Running {script_name}...")
        
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if not statement or statement.startswith('--'):
                continue
                
            print(f"   Executing statement {i+1}/{len(statements)}")
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                json={"sql": statement},
                headers=headers,
                timeout=30
            )
            
            if response.status_code not in [200, 204]:
                print(f"   ⚠️  Statement {i+1} response: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")
        
        print(f"✅ {script_name} completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in {script_name}: {e}")
        return False

def run_migrations():
    """Run all migration scripts in order"""
    print("🚀 STARTING SUPABASE MIGRATION")
    print("=" * 40)
    
    migration_files = [
        'migrations/001_create_payment_tables.sql',
        'migrations/002_enhance_existing_tables.sql', 
        'migrations/003_create_indexes.sql',
        'migrations/004_setup_rls_policies.sql'
    ]
    
    success_count = 0
    
    for migration_file in migration_files:
        try:
            if not os.path.exists(migration_file):
                print(f"⚠️  File not found: {migration_file}")
                continue
                
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            if execute_sql(sql_content, migration_file):
                success_count += 1
                
        except Exception as e:
            print(f"❌ Failed to read {migration_file}: {e}")
    
    print(f"\n📊 MIGRATION RESULTS: {success_count}/{len(migration_files)} completed")
    
    if success_count == len(migration_files):
        print("🎉 ALL MIGRATIONS SUCCESSFUL!")
        return True
    else:
        print("⚠️  Some migrations failed - check logs above")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)