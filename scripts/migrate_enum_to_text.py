#!/usr/bin/env python3
"""
Script to migrate PostgreSQL report_type column from ENUM to TEXT
This allows storing arbitrary report titles extracted from PDFs
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

def migrate_postgresql():
    """Migrate PostgreSQL database from ENUM to TEXT"""
    print(f"🔄 Migrating PostgreSQL database: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                print("📝 Step 1: Adding temporary TEXT column...")
                conn.execute(text("ALTER TABLE reports ADD COLUMN report_type_new TEXT;"))
                
                print("📝 Step 2: Copying data from ENUM to TEXT column...")
                conn.execute(text("UPDATE reports SET report_type_new = report_type::TEXT;"))
                
                print("📝 Step 3: Dropping old ENUM column...")
                conn.execute(text("ALTER TABLE reports DROP COLUMN report_type;"))
                
                print("📝 Step 4: Renaming new column to report_type...")
                conn.execute(text("ALTER TABLE reports RENAME COLUMN report_type_new TO report_type;"))
                
                print("📝 Step 5: Adding NOT NULL constraint...")
                conn.execute(text("ALTER TABLE reports ALTER COLUMN report_type SET NOT NULL;"))
                
                print("📝 Step 6: Dropping the old ENUM type...")
                # First check if any other tables use this enum
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.columns 
                    WHERE udt_name = 'reporttypeenum'
                """))
                count = result.scalar()
                
                if count == 0:
                    conn.execute(text("DROP TYPE IF EXISTS reporttypeenum;"))
                    print("✅ Dropped old ENUM type")
                else:
                    print("⚠️  ENUM type still in use by other columns, not dropping")
                
                # Commit the transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during migration: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    return True

def migrate_sqlite():
    """For SQLite, we don't have ENUMs, so this is a no-op"""
    print("✅ SQLite database - no ENUM migration needed")
    return True

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print(f"Database URL: {DATABASE_URL}")
    
    if DATABASE_URL.startswith("postgresql"):
        success = migrate_postgresql()
    elif DATABASE_URL.startswith("sqlite"):
        success = migrate_sqlite()
    else:
        print(f"❌ Unsupported database type: {DATABASE_URL}")
        success = False
    
    if success:
        print("\n🎉 Migration completed! The database now supports arbitrary report titles.")
        print("You can now restart the backend server.")
    else:
        print("\n💥 Migration failed! Please check the errors above.")
        sys.exit(1)
