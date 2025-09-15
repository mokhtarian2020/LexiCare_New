#!/usr/bin/env python3
"""
Migration script to convert report_type column from ENUM to TEXT in PostgreSQL.
This fixes the critical issue where arbitrary report titles cannot be stored.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def get_database_url():
    """Get the database URL from environment variables."""
    return os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

def migrate_report_type_to_text():
    """
    Migrate the report_type column from ENUM to TEXT.
    This will allow storing any arbitrary report title.
    """
    database_url = get_database_url()
    print(f"🔄 Connecting to database: {database_url}")
    
    try:
        # Parse the database URL to get connection parameters
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Check current column type
        cursor.execute("""
            SELECT data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'reports' AND column_name = 'report_type'
        """)
        current_type = cursor.fetchone()
        
        if current_type:
            print(f"📋 Current report_type column type: {current_type[0]} ({current_type[1]})")
            
            if current_type[1] == 'reporttypeenum':
                print("🔄 Converting report_type column from ENUM to TEXT...")
                
                # Step 1: Add a temporary column
                cursor.execute("ALTER TABLE reports ADD COLUMN report_type_temp TEXT")
                print("✅ Added temporary TEXT column")
                
                # Step 2: Copy data from ENUM to TEXT
                cursor.execute("UPDATE reports SET report_type_temp = report_type::TEXT")
                print("✅ Copied data to temporary column")
                
                # Step 3: Drop the old ENUM column
                cursor.execute("ALTER TABLE reports DROP COLUMN report_type")
                print("✅ Dropped old ENUM column")
                
                # Step 4: Rename the temporary column
                cursor.execute("ALTER TABLE reports RENAME COLUMN report_type_temp TO report_type")
                print("✅ Renamed temporary column to report_type")
                
                # Step 5: Drop the ENUM type if it exists and is not used elsewhere
                try:
                    cursor.execute("DROP TYPE IF EXISTS reporttypeenum")
                    print("✅ Dropped unused ENUM type")
                except Exception as e:
                    print(f"⚠️  Could not drop ENUM type (might be in use elsewhere): {e}")
                
                print("🎉 Migration completed successfully!")
                
            elif current_type[0] == 'text':
                print("✅ Column is already TEXT type, no migration needed")
            else:
                print(f"⚠️  Unexpected column type: {current_type}")
        else:
            print("❌ report_type column not found in reports table")
            return False
        
        # Verify the migration
        cursor.execute("""
            SELECT data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'reports' AND column_name = 'report_type'
        """)
        new_type = cursor.fetchone()
        print(f"✅ Final report_type column type: {new_type[0]} ({new_type[1]})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting report_type column migration...")
    success = migrate_report_type_to_text()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("🔄 Please restart your backend server to apply the changes.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
