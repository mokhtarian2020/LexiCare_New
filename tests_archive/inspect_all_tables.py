#!/usr/bin/env python3
"""
Script to inspect ALL tables in the LexiCare database and show raw content
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import sqlite3

# Change to backend directory for imports to work
script_dir = Path(__file__).parent
backend_dir = script_dir / "backend"
original_cwd = os.getcwd()

# Temporarily change to backend directory
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

try:
    from db.session import SessionLocal
    from db.models import Report
    from sqlalchemy import text, inspect
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def get_database_path():
    """Get the path to the SQLite database"""
    return backend_dir / "db" / "lexicare.db"

def inspect_with_sqlalchemy():
    """Inspect database using SQLAlchemy"""
    print("🔍 DATABASE INSPECTION WITH SQLALCHEMY")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get database inspector
        inspector = inspect(db.bind)
        
        # Get all table names
        table_names = inspector.get_table_names()
        print(f"📊 Found {len(table_names)} tables: {table_names}")
        
        for table_name in table_names:
            print(f"\n📋 TABLE: {table_name}")
            print("-" * 40)
            
            # Get table columns
            columns = inspector.get_columns(table_name)
            print("📝 Columns:")
            for col in columns:
                print(f"    {col['name']} ({col['type']}) - Nullable: {col['nullable']}")
            
            # Get row count
            result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"📊 Total rows: {count}")
            
            # Show sample data
            if count > 0:
                print("\n📄 Sample data (first 3 rows):")
                result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                rows = result.fetchall()
                column_names = result.keys()
                
                for i, row in enumerate(rows, 1):
                    print(f"\n  Row {i}:")
                    for col_name, value in zip(column_names, row):
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 100:
                            display_value = value[:100] + "..."
                        else:
                            display_value = value
                        print(f"    {col_name}: {display_value}")
            
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"❌ Error with SQLAlchemy inspection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def inspect_with_sqlite():
    """Inspect database using direct SQLite connection"""
    print("\n🔍 RAW DATABASE INSPECTION WITH SQLITE")
    print("=" * 60)
    
    db_path = get_database_path()
    
    if not db_path.exists():
        print(f"❌ Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables in SQLite database")
        
        for (table_name,) in tables:
            print(f"\n📋 TABLE: {table_name}")
            print("-" * 40)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()
            
            print("📝 Schema:")
            for col_info in schema:
                cid, name, col_type, notnull, default_val, pk = col_info
                nullable = "NOT NULL" if notnull else "NULL"
                primary = " (PRIMARY KEY)" if pk else ""
                print(f"    {name}: {col_type} {nullable}{primary}")
                if default_val is not None:
                    print(f"        DEFAULT: {default_val}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"📊 Total rows: {count}")
            
            # Show ALL data for small tables, or sample for large tables
            if count > 0:
                if count <= 10:
                    print(f"\n📄 ALL DATA ({count} rows):")
                    cursor.execute(f"SELECT * FROM {table_name};")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for i, row in enumerate(rows, 1):
                        print(f"\n  📄 Row {i}:")
                        for col_name, value in zip(columns, row):
                            # Format value for display
                            if isinstance(value, str) and len(value) > 200:
                                display_value = value[:200] + "... (truncated)"
                            else:
                                display_value = value
                            print(f"    {col_name}: {display_value}")
                else:
                    print(f"\n📄 SAMPLE DATA (first 5 rows out of {count}):")
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for i, row in enumerate(rows, 1):
                        print(f"\n  📄 Row {i}:")
                        for col_name, value in zip(columns, row):
                            # Format value for display
                            if isinstance(value, str) and len(value) > 200:
                                display_value = value[:200] + "... (truncated)"
                            else:
                                display_value = value
                            print(f"    {col_name}: {display_value}")
            
            print("\n" + "=" * 60)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error with SQLite inspection: {e}")
        import traceback
        traceback.print_exc()

def show_reports_table_detailed():
    """Show detailed view of reports table specifically"""
    print("\n🔍 DETAILED REPORTS TABLE INSPECTION")
    print("=" * 60)
    
    db_path = get_database_path()
    
    if not db_path.exists():
        print(f"❌ Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if reports table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports';")
        if not cursor.fetchone():
            print("❌ Reports table not found!")
            return
        
        # Get all reports
        cursor.execute("SELECT * FROM reports ORDER BY created_at;")
        reports = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(reports);")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Total reports: {len(reports)}")
        print(f"📝 Columns: {', '.join(columns)}")
        
        if not reports:
            print("📝 No reports found in database")
            return
        
        for i, report in enumerate(reports, 1):
            print(f"\n📋 REPORT #{i}")
            print("-" * 40)
            
            for col_name, value in zip(columns, report):
                # Special formatting for different field types
                if col_name in ['extracted_text'] and value and len(str(value)) > 300:
                    display_value = str(value)[:300] + "... (truncated)"
                elif col_name in ['ai_diagnosis', 'comparison_explanation'] and value and len(str(value)) > 150:
                    display_value = str(value)[:150] + "... (truncated)"
                else:
                    display_value = value
                
                print(f"  {col_name}: {display_value}")
            
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def show_raw_sql_queries():
    """Show some useful raw SQL queries"""
    print("\n🔍 USEFUL RAW SQL QUERIES")
    print("=" * 40)
    
    db_path = get_database_path()
    
    if not db_path.exists():
        print(f"❌ Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        queries = [
            ("List all tables", "SELECT name FROM sqlite_master WHERE type='table';"),
            ("Count all reports", "SELECT COUNT(*) FROM reports;"),
            ("Reports by type", "SELECT report_type, COUNT(*) FROM reports GROUP BY report_type;"),
            ("Recent reports", "SELECT patient_name, report_type, created_at FROM reports ORDER BY created_at DESC LIMIT 5;"),
            ("Patients with multiple reports", "SELECT patient_cf, patient_name, COUNT(*) as count FROM reports GROUP BY patient_cf HAVING COUNT(*) > 1;"),
        ]
        
        for title, query in queries:
            print(f"\n📊 {title}:")
            print(f"SQL: {query}")
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                for row in results:
                    print(f"  {row}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🗄️ LEXICARE DATABASE COMPLETE INSPECTION")
    print("=" * 80)
    print(f"📍 Database location: {get_database_path()}")
    print(f"📅 Inspection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all inspections
    inspect_with_sqlalchemy()
    inspect_with_sqlite()
    show_reports_table_detailed()
    show_raw_sql_queries()
    
    print("\n✅ Database inspection complete!")
