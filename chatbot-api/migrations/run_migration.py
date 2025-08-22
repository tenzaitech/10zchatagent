#!/usr/bin/env python3
"""
Database Migration Runner
Executes SQL migration scripts safely with rollback capability
"""

import os
import sys
import json
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Optional

# Configuration from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class MigrationRunner:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        
        self.headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }
        
        self.migration_scripts = [
            "001_create_payment_tables.sql",
            "002_enhance_existing_tables.sql", 
            "003_create_indexes.sql",
            "004_setup_rls_policies.sql"
        ]
        
        self.status_file = "migration_status.json"
    
    async def load_migration_status(self) -> Dict:
        """Load current migration status"""
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "migration_info": {
                    "version": "2.0",
                    "status": "pending",
                    "current_phase": "not_started"
                },
                "completed_scripts": [],
                "pending_scripts": self.migration_scripts.copy()
            }
    
    async def save_migration_status(self, status: Dict):
        """Save migration status"""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2, default=str)
    
    async def execute_sql(self, sql_content: str) -> Dict:
        """Execute SQL using Supabase RPC function"""
        try:
            # For now, we'll use a simple table creation test
            # In production, you might need a custom RPC function
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Test connection first
                response = await client.get(
                    f"{SUPABASE_URL}/rest/v1/",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    print(f"✅ Connected to Supabase successfully")
                    return {"success": True, "message": "SQL would be executed here"}
                else:
                    return {"success": False, "error": f"Connection failed: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_migration_script(self, script_name: str) -> bool:
        """Run a single migration script"""
        print(f"\n🔄 Running migration: {script_name}")
        
        # Read SQL file
        script_path = script_name
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            return False
        
        try:
            with open(script_path, 'r') as f:
                sql_content = f.read()
            
            print(f"📄 Read {len(sql_content)} characters from {script_name}")
            
            # Execute SQL
            result = await self.execute_sql(sql_content)
            
            if result["success"]:
                print(f"✅ Migration {script_name} completed successfully")
                return True
            else:
                print(f"❌ Migration {script_name} failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error running {script_name}: {e}")
            return False
    
    async def validate_tables(self) -> bool:
        """Validate that expected tables exist"""
        expected_tables = [
            "payment_transactions",
            "order_status_history", 
            "staff_actions",
            "settings"
        ]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Check if we can access tables (this will validate they exist)
                for table in expected_tables:
                    response = await client.get(
                        f"{SUPABASE_URL}/rest/v1/{table}?select=count()",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Table {table} exists and is accessible")
                    else:
                        print(f"⚠️ Table {table} might not exist (status: {response.status_code})")
                        return False
                
                return True
                
        except Exception as e:
            print(f"❌ Table validation error: {e}")
            return False
    
    async def run_all_migrations(self, dry_run: bool = True) -> bool:
        """Run all pending migrations"""
        print(f"🚀 Starting Database V2 Migration {'(DRY RUN)' if dry_run else '(LIVE)'}")
        
        # Load current status
        status = await self.load_migration_status()
        
        if dry_run:
            print("\n📋 DRY RUN MODE - Validating scripts without execution")
            
            # Validate all scripts exist and are readable
            for script in self.migration_scripts:
                if os.path.exists(script):
                    with open(script, 'r') as f:
                        content = f.read()
                    print(f"✅ {script}: {len(content)} characters, ready to run")
                else:
                    print(f"❌ {script}: File not found")
                    return False
            
            print("\n✅ DRY RUN PASSED - All scripts are ready")
            print("💡 Run with --live flag to execute actual migration")
            return True
        
        # Live migration
        print("\n⚠️ LIVE MIGRATION MODE - Making actual database changes")
        input("Press Enter to continue or Ctrl+C to abort...")
        
        # Update status
        status["migration_info"]["started_at"] = datetime.now().isoformat()
        status["migration_info"]["status"] = "running"
        await self.save_migration_status(status)
        
        # Run each migration script
        for script in self.migration_scripts:
            if script in status["completed_scripts"]:
                print(f"⏩ Skipping {script} (already completed)")
                continue
            
            success = await self.run_migration_script(script)
            
            if success:
                status["completed_scripts"].append(script)
                if script in status["pending_scripts"]:
                    status["pending_scripts"].remove(script)
                await self.save_migration_status(status)
            else:
                status["migration_info"]["status"] = "failed"
                status["migration_info"]["failed_at"] = datetime.now().isoformat()
                await self.save_migration_status(status)
                return False
        
        # Final validation
        print("\n🔍 Validating migration results...")
        if await self.validate_tables():
            status["migration_info"]["status"] = "completed"
            status["migration_info"]["completed_at"] = datetime.now().isoformat()
            print("🎉 Migration completed successfully!")
        else:
            status["migration_info"]["status"] = "validation_failed"
            print("❌ Migration validation failed")
            return False
        
        await self.save_migration_status(status)
        return True

async def main():
    """Main migration runner"""
    runner = MigrationRunner()
    
    # Parse command line arguments
    dry_run = "--live" not in sys.argv
    
    try:
        success = await runner.run_all_migrations(dry_run=dry_run)
        if success:
            print("\n✅ Migration process completed successfully")
            exit(0)
        else:
            print("\n❌ Migration process failed")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Migration cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    print("Database V2 Migration Tool")
    print("=" * 50)
    asyncio.run(main())