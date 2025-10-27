#!/usr/bin/env python3
"""
Quick database query script for LexiCare
"""

import sys
import os
from pathlib import Path

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
    from sqlalchemy import text
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def run_custom_query(query):
    """Run a custom SQL query"""
    db = SessionLocal()
    try:
        result = db.execute(text(query)).fetchall()
        return result
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        return None
    finally:
        db.close()

def show_table_schema():
    """Show the table schema"""
    query = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'reports'
    ORDER BY ordinal_position;
    """
    
    print("📋 Database Schema for 'reports' table:")
    print("-" * 60)
    print(f"{'Column Name':<25} {'Data Type':<20} {'Nullable':<10} {'Default'}")
    print("-" * 60)
    
    result = run_custom_query(query)
    if result:
        for row in result:
            col_name, data_type, is_nullable, col_default = row
            default_str = str(col_default)[:15] + "..." if col_default and len(str(col_default)) > 15 else str(col_default)
            print(f"{col_name:<25} {data_type:<20} {is_nullable:<10} {default_str}")

def show_all_patients():
    """Show all unique patients"""
    query = """
    SELECT DISTINCT patient_cf, patient_name, COUNT(*) as report_count
    FROM reports 
    GROUP BY patient_cf, patient_name
    ORDER BY patient_name;
    """
    
    print("👥 All Patients in Database:")
    print("-" * 50)
    
    result = run_custom_query(query)
    if result:
        for row in result:
            cf, name, count = row
            print(f"🆔 {cf} - 👤 {name} ({count} reports)")

def show_report_summary():
    """Show a summary of all reports"""
    query = """
    SELECT 
        id,
        patient_name,
        patient_cf,
        report_type,
        report_category,
        ai_classification,
        report_date,
        created_at
    FROM reports 
    ORDER BY created_at DESC;
    """
    
    print("📊 All Reports Summary:")
    print("-" * 80)
    
    result = run_custom_query(query)
    if result:
        for i, row in enumerate(result, 1):
            report_id, name, cf, rtype, category, classification, rdate, created = row
            print(f"\n📋 Report #{i}")
            print(f"   🆔 ID: {report_id}")
            print(f"   👤 Patient: {name} ({cf})")
            print(f"   📝 Type: {rtype}")
            print(f"   📂 Category: {category}")
            print(f"   📈 Classification: {classification}")
            print(f"   📅 Report Date: {rdate}")
            print(f"   🕒 Created: {created}")

def show_ai_diagnoses():
    """Show all AI diagnoses"""
    query = """
    SELECT 
        patient_name,
        report_type,
        ai_diagnosis,
        ai_classification,
        report_date
    FROM reports 
    ORDER BY report_date DESC;
    """
    
    print("🤖 AI Diagnoses:")
    print("-" * 60)
    
    result = run_custom_query(query)
    if result:
        for row in result:
            name, rtype, diagnosis, classification, rdate = row
            print(f"\n👤 {name} - {rdate}")
            print(f"   📝 {rtype}")
            print(f"   🩺 {diagnosis}")
            print(f"   📈 {classification}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--schema":
            show_table_schema()
        elif command == "--patients":
            show_all_patients()
        elif command == "--summary":
            show_report_summary()
        elif command == "--diagnoses":
            show_ai_diagnoses()
        elif command == "--query" and len(sys.argv) > 2:
            custom_query = " ".join(sys.argv[2:])
            print(f"🔍 Executing: {custom_query}")
            print("-" * 40)
            result = run_custom_query(custom_query)
            if result:
                for row in result:
                    print(row)
        else:
            print("Usage:")
            print("  python quick_db_query.py --schema      # Show table schema")
            print("  python quick_db_query.py --patients    # Show all patients")
            print("  python quick_db_query.py --summary     # Show report summary")
            print("  python quick_db_query.py --diagnoses   # Show AI diagnoses")
            print("  python quick_db_query.py --query 'SELECT * FROM reports;'")
    else:
        print("🔍 LexiCare Database Quick Query Tool")
        print("=" * 40)
        print("Available commands:")
        print("  --schema      Show table schema")
        print("  --patients    Show all patients")
        print("  --summary     Show report summary")
        print("  --diagnoses   Show AI diagnoses")
        print("  --query 'SQL' Run custom SQL query")
        print("\nFor detailed inspection, use: python inspect_database.py")
