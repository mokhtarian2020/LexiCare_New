#!/usr/bin/env python3
"""
Script to migrate database from report_title to tipo_referto
This script will:
1. Add the new tipo_referto column
2. Copy data from report_title to tipo_referto 
3. Drop the old report_title column
"""

import os
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

def migrate_sqlite():
    """Migrate SQLite database"""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist. Nothing to migrate.")
        return
    
    print(f"Migrating SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if report_title column exists
        cursor.execute("PRAGMA table_info(reports)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'report_title' not in column_names:
            print("Column 'report_title' not found. Migration may have already been completed.")
            return
            
        if 'tipo_referto' in column_names:
            print("Column 'tipo_referto' already exists. Skipping migration.")
            return
        
        print("Adding tipo_referto column...")
        cursor.execute("ALTER TABLE reports ADD COLUMN tipo_referto TEXT")
        
        print("Copying data from report_title to tipo_referto...")
        cursor.execute("UPDATE reports SET tipo_referto = report_title")
        
        print("Setting tipo_referto as NOT NULL...")
        # For SQLite, we need to recreate the table to add NOT NULL constraint
        # First, create a backup table
        cursor.execute("""
            CREATE TABLE reports_backup AS 
            SELECT id, patient_cf, patient_name, tipo_referto, report_date, 
                   file_path, extracted_text, ai_diagnosis, ai_classification,
                   doctor_diagnosis, doctor_classification, doctor_comment,
                   comparison_to_previous, comparison_explanation, created_at
            FROM reports
        """)
        
        # Drop the original table
        cursor.execute("DROP TABLE reports")
        
        # Recreate the table with proper schema
        cursor.execute("""
            CREATE TABLE reports (
                id TEXT PRIMARY KEY,
                patient_cf TEXT NOT NULL,
                patient_name TEXT,
                tipo_referto TEXT NOT NULL,
                report_date DATETIME NOT NULL,
                file_path TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                ai_diagnosis TEXT NOT NULL,
                ai_classification TEXT NOT NULL,
                doctor_diagnosis TEXT,
                doctor_classification TEXT,
                doctor_comment TEXT,
                comparison_to_previous TEXT,
                comparison_explanation TEXT,
                created_at DATETIME
            )
        """)
        
        # Copy data back
        cursor.execute("""
            INSERT INTO reports 
            SELECT * FROM reports_backup
        """)
        
        # Drop backup table
        cursor.execute("DROP TABLE reports_backup")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

def migrate_postgresql():
    """Migrate PostgreSQL database"""
    print(f"Migrating PostgreSQL database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reports'
            """))
            columns = [row[0] for row in result]
            
            if 'report_title' not in columns:
                print("Column 'report_title' not found. Migration may have already been completed.")
                return
                
            if 'tipo_referto' in columns:
                print("Column 'tipo_referto' already exists. Skipping migration.")
                return
            
            print("Adding tipo_referto column...")
            conn.execute(text("ALTER TABLE reports ADD COLUMN tipo_referto TEXT"))
            
            print("Copying data from report_title to tipo_referto...")
            conn.execute(text("UPDATE reports SET tipo_referto = report_title"))
            
            print("Setting tipo_referto as NOT NULL...")
            conn.execute(text("ALTER TABLE reports ALTER COLUMN tipo_referto SET NOT NULL"))
            
            print("Dropping report_title column...")
            conn.execute(text("ALTER TABLE reports DROP COLUMN report_title"))
            
            conn.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    if DATABASE_URL.startswith("sqlite"):
        migrate_sqlite()
    else:
        migrate_postgresql()
