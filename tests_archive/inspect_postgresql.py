#!/usr/bin/env python3
"""
Script to inspect PostgreSQL database used by LexiCare
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Change to backend directory for imports to work
script_dir = Path(__file__).parent
backend_dir = script_dir / "backend"
original_cwd = os.getcwd()

# Temporarily change to backend directory
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

try:
    from db.session import SessionLocal, engine
    from db.models import Report
    from sqlalchemy import text, inspect
    import sqlalchemy
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def inspect_postgresql_database():
    """Inspect the PostgreSQL database"""
    print("🐘 POSTGRESQL DATABASE INSPECTION")
    print("=" * 60)
    
    # Check connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return
    
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
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"    {col['name']}: {col['type']} ({nullable})")
            
            # Get row count
            result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"📊 Total rows: {count}")
            
            # Show data
            if count > 0:
                print(f"\n📄 ALL DATA ({count} rows):")
                result = db.execute(text(f"SELECT * FROM {table_name} ORDER BY created_at"))
                rows = result.fetchall()
                column_names = result.keys()
                
                for i, row in enumerate(rows, 1):
                    print(f"\n  📄 Row {i}:")
                    for col_name, value in zip(column_names, row):
                        # Format value for display
                        if col_name == 'extracted_text' and value and len(str(value)) > 300:
                            display_value = str(value)[:300] + "... (truncated)"
                        elif col_name in ['ai_diagnosis', 'comparison_explanation'] and value and len(str(value)) > 150:
                            display_value = str(value)[:150] + "... (truncated)"
                        else:
                            display_value = value
                        print(f"    {col_name}: {display_value}")
            
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def show_feedback_data():
    """Show feedback data specifically"""
    print("\n🔍 FEEDBACK DATA INSPECTION")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        # Query all reports with feedback data
        result = db.execute(text("""
            SELECT 
                id,
                patient_name,
                patient_cf,
                report_type,
                report_date,
                ai_diagnosis,
                ai_classification,
                doctor_diagnosis,
                doctor_classification,
                doctor_comment,
                comparison_to_previous,
                created_at
            FROM reports 
            WHERE doctor_diagnosis IS NOT NULL 
               OR doctor_classification IS NOT NULL 
               OR doctor_comment IS NOT NULL
            ORDER BY created_at
        """))
        
        feedback_reports = result.fetchall()
        column_names = result.keys()
        
        print(f"📊 Reports with feedback: {len(feedback_reports)}")
        
        if feedback_reports:
            for i, report in enumerate(feedback_reports, 1):
                print(f"\n📋 FEEDBACK REPORT #{i}")
                print("-" * 30)
                for col_name, value in zip(column_names, report):
                    print(f"  {col_name}: {value}")
        else:
            print("📝 No reports with feedback found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def show_comparison_data():
    """Show comparison data specifically"""
    print("\n🔍 COMPARISON DATA INSPECTION")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        # Query all reports with comparison data
        result = db.execute(text("""
            SELECT 
                id,
                patient_name,
                patient_cf,
                report_type,
                report_date,
                comparison_to_previous,
                comparison_explanation,
                created_at
            FROM reports 
            WHERE comparison_to_previous IS NOT NULL 
               OR comparison_explanation IS NOT NULL
            ORDER BY patient_cf, report_date
        """))
        
        comparison_reports = result.fetchall()
        column_names = result.keys()
        
        print(f"📊 Reports with comparison data: {len(comparison_reports)}")
        
        if comparison_reports:
            for i, report in enumerate(comparison_reports, 1):
                print(f"\n📋 COMPARISON REPORT #{i}")
                print("-" * 30)
                for col_name, value in zip(column_names, report):
                    if col_name == 'comparison_explanation' and value and len(str(value)) > 200:
                        display_value = str(value)[:200] + "... (truncated)"
                    else:
                        display_value = value
                    print(f"  {col_name}: {display_value}")
        else:
            print("📝 No reports with comparison data found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def show_patient_summary():
    """Show summary by patient"""
    print("\n🔍 PATIENT SUMMARY")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        # Get patient summary
        result = db.execute(text("""
            SELECT 
                patient_cf,
                patient_name,
                COUNT(*) as total_reports,
                MIN(report_date) as earliest_report,
                MAX(report_date) as latest_report,
                MIN(created_at) as first_upload,
                MAX(created_at) as last_upload
            FROM reports 
            GROUP BY patient_cf, patient_name
            ORDER BY patient_cf
        """))
        
        patients = result.fetchall()
        column_names = result.keys()
        
        print(f"📊 Total patients: {len(patients)}")
        
        for i, patient in enumerate(patients, 1):
            print(f"\n👤 PATIENT #{i}")
            print("-" * 20)
            for col_name, value in zip(column_names, patient):
                print(f"  {col_name}: {value}")
            
            # Get report details for this patient
            patient_cf = patient[0]
            result2 = db.execute(text("""
                SELECT report_type, report_date, ai_diagnosis, comparison_to_previous
                FROM reports 
                WHERE patient_cf = :cf
                ORDER BY report_date
            """), {"cf": patient_cf})
            
            reports = result2.fetchall()
            print(f"  📋 Reports:")
            for j, (rtype, rdate, diagnosis, comparison) in enumerate(reports, 1):
                print(f"    {j}. {rtype} ({rdate}) - {diagnosis[:50]}... - {comparison}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🗄️ LEXICARE POSTGRESQL DATABASE INSPECTION")
    print("=" * 80)
    print(f"📅 Inspection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all inspections
    inspect_postgresql_database()
    show_feedback_data()
    show_comparison_data()
    show_patient_summary()
    
    print("\n✅ PostgreSQL database inspection complete!")
