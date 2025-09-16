#!/usr/bin/env python3
"""
Script to completely reset the database schema.
This will:
1. Drop all existing tables
2. Recreate tables with the correct schema (using patient_cf instead of patient_id)
3. Ensure clean start with no legacy schema issues
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def reset_postgresql_database():
    """Reset PostgreSQL database completely"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url or not database_url.startswith("postgresql"):
        print("❌ This script is for PostgreSQL databases only")
        return False
    
    print(f"🔄 Resetting PostgreSQL database: {database_url}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("📋 Getting list of existing tables...")
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public';
        """)
        tables = cur.fetchall()
        
        # Drop all existing tables
        if tables:
            print(f"🗑️ Dropping {len(tables)} existing tables...")
            for (table_name,) in tables:
                print(f"   - Dropping table: {table_name}")
                cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        else:
            print("ℹ️ No existing tables found")
        
        # Drop any existing ENUMs that might cause issues
        print("🗑️ Dropping any existing ENUM types...")
        cur.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT typname FROM pg_type WHERE typtype = 'e') LOOP
                    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        
        cur.close()
        conn.close()
        
        print("✅ Database reset complete - all tables and types dropped")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        return False

def recreate_schema():
    """Recreate the database schema with correct models"""
    print("🔄 Recreating database schema...")
    
    try:
        # Import and initialize the database with correct schema
        from backend.db.session import init_db
        init_db()
        print("✅ Database schema recreated successfully")
        return True
    except Exception as e:
        print(f"❌ Error recreating schema: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting complete database reset...")
    print("⚠️ WARNING: This will delete ALL existing data!")
    
    # Reset the database
    if reset_postgresql_database():
        # Recreate with correct schema
        if recreate_schema():
            print("🎉 Database reset and recreation completed successfully!")
            print("📝 The database now uses 'patient_cf' instead of 'patient_id'")
        else:
            print("❌ Failed to recreate schema")
    else:
        print("❌ Failed to reset database")
