#!/usr/bin/env python3
"""
Script to inspect the LexiCare database and view all reports
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
    from db.session import SessionLocal
    from db.models import Report
    from sqlalchemy import text, inspect
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def format_json_field(json_str):
    """Format JSON field for better readability"""
    if not json_str:
        return "None"
    try:
        data = json.loads(json_str) if isinstance(json_str, str) else json_str
        if isinstance(data, dict):
            # Format key findings nicely
            formatted = []
            for key, value in data.items():
                if isinstance(value, dict):
                    formatted.append(f"{key}: {value}")
                else:
                    formatted.append(f"{key}: {value}")
            return "\n    ".join(formatted)
        return str(data)
    except:
        return str(json_str)

def view_all_reports():
    """View all reports in the database with detailed information"""
    
    print("🔍 LexiCare Database Inspector")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Get total count
        total_reports = db.query(Report).count()
        print(f"📊 Total Reports in Database: {total_reports}")
        
        if total_reports == 0:
            print("📝 No reports found in the database")
            return
        
        print("\n" + "=" * 80)
        
        # Get all reports ordered by creation date
        reports = db.query(Report).order_by(Report.created_at).all()
        
        for i, report in enumerate(reports, 1):
            print(f"\n📋 REPORT #{i}")
            print("-" * 40)
            print(f"🆔 ID: {report.id}")
            print(f"👤 Patient Name: {report.patient_name}")
            print(f"🆔 Codice Fiscale: {report.patient_cf}")
            print(f"📅 Report Date: {report.report_date}")
            print(f"📝 Report Type: {report.report_type}")
            print(f"📂 Report Category: {getattr(report, 'report_category', 'N/A')}")
            print(f"💾 File Path: {report.file_path}")
            print(f"� Created At: {report.created_at}")
            
            # Format AI diagnosis
            print(f"\n🩺 AI Diagnosis:")
            if hasattr(report, 'ai_diagnosis') and report.ai_diagnosis:
                print(f"    {report.ai_diagnosis}")
            else:
                print("    None")
            
            # Format AI classification
            print(f"\n� AI Classification:")
            if hasattr(report, 'ai_classification') and report.ai_classification:
                print(f"    {report.ai_classification}")
            else:
                print("    None")
            
            # Format doctor diagnosis
            print(f"\n👨‍⚕️ Doctor Diagnosis:")
            if hasattr(report, 'doctor_diagnosis') and report.doctor_diagnosis:
                print(f"    {report.doctor_diagnosis}")
            else:
                print("    None")
            
            # Format doctor classification
            print(f"\n�‍⚕️ Doctor Classification:")
            if hasattr(report, 'doctor_classification') and report.doctor_classification:
                print(f"    {report.doctor_classification}")
            else:
                print("    None")
            
            # Format comparison to previous
            print(f"\n📊 Comparison to Previous:")
            if hasattr(report, 'comparison_to_previous') and report.comparison_to_previous:
                print(f"    {report.comparison_to_previous}")
            else:
                print("    None")
            
            # Format comparison explanation
            print(f"\n� Comparison Explanation:")
            if hasattr(report, 'comparison_explanation') and report.comparison_explanation:
                print(f"    {report.comparison_explanation}")
            else:
                print("    None")
                
            # Format extracted text (first 200 chars)
            print(f"\n📄 Extracted Text (preview):")
            if hasattr(report, 'extracted_text') and report.extracted_text:
                preview = report.extracted_text[:200] + "..." if len(report.extracted_text) > 200 else report.extracted_text
                print(f"    {preview}")
            else:
                print("    None")
            
            print("\n" + "=" * 80)
        
        # Summary statistics
        print(f"\n📈 SUMMARY STATISTICS")
        print("-" * 30)
        
        # Count by report type
        type_counts = db.execute(text("""
            SELECT report_type, COUNT(*) as count 
            FROM reports 
            GROUP BY report_type
        """)).fetchall()
        
        print("📋 Reports by Type:")
        for row in type_counts:
            print(f"    {row[0]}: {row[1]} reports")
        
        # Count by AI classification
        class_counts = db.execute(text("""
            SELECT ai_classification, COUNT(*) as count 
            FROM reports 
            WHERE ai_classification IS NOT NULL
            GROUP BY ai_classification
        """)).fetchall()
        
        print("\n📊 Reports by AI Classification:")
        for row in class_counts:
            print(f"    {row[0]}: {row[1]} reports")
        
        # Count by patient (Codice Fiscale)
        patient_counts = db.execute(text("""
            SELECT patient_cf, patient_name, COUNT(*) as report_count 
            FROM reports 
            GROUP BY patient_cf, patient_name
            ORDER BY report_count DESC
        """)).fetchall()
        
        print(f"\n👥 Reports by Patient:")
        for row in patient_counts:
            print(f"    {row[1]} ({row[0]}): {row[2]} reports")
        
        # Recent activity
        recent_reports = db.execute(text("""
            SELECT patient_name, report_type, ai_classification, created_at
            FROM reports 
            ORDER BY created_at DESC 
            LIMIT 5
        """)).fetchall()
        
        print(f"\n🕒 Recent Activity (Last 5 reports):")
        for row in recent_reports:
            created_date = row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else "Unknown"
            print(f"    {created_date} - {row[0]} ({row[1]}) - {row[2]}")
            
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def view_specific_patient(codice_fiscale):
    """View all reports for a specific patient"""
    
    print(f"🔍 Reports for Patient: {codice_fiscale}")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        reports = db.query(Report).filter(
            Report.patient_cf == codice_fiscale
        ).order_by(Report.report_date).all()
        
        if not reports:
            print(f"📝 No reports found for Codice Fiscale: {codice_fiscale}")
            return
        
        print(f"📊 Found {len(reports)} reports for this patient")
        print(f"👤 Patient Name: {reports[0].patient_name}")
        
        for i, report in enumerate(reports, 1):
            print(f"\n📋 Report #{i} - {report.report_date}")
            print(f"📝 Type: {report.report_type}")
            print(f"📈 AI Classification: {report.ai_classification}")
            
            if hasattr(report, 'ai_diagnosis') and report.ai_diagnosis:
                print(f"🩺 AI Diagnosis: {report.ai_diagnosis}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

def check_data_integrity():
    """Check for data integrity issues"""
    
    print("🔍 Data Integrity Check")
    print("=" * 30)
    
    db = SessionLocal()
    try:
        # Check for missing required fields
        issues = []
        
        reports_missing_cf = db.query(Report).filter(
            (Report.patient_cf == None) | (Report.patient_cf == "")
        ).count()
        
        if reports_missing_cf > 0:
            issues.append(f"📋 {reports_missing_cf} reports missing Codice Fiscale")
        
        reports_missing_name = db.query(Report).filter(
            (Report.patient_name == None) | (Report.patient_name == "")
        ).count()
        
        if reports_missing_name > 0:
            issues.append(f"👤 {reports_missing_name} reports missing patient name")
        
        reports_missing_type = db.query(Report).filter(
            (Report.report_type == None) | (Report.report_type == "")
        ).count()
        
        if reports_missing_type > 0:
            issues.append(f"📝 {reports_missing_type} reports missing report type")
        
        reports_missing_date = db.query(Report).filter(
            Report.report_date == None
        ).count()
        
        if reports_missing_date > 0:
            issues.append(f"📅 {reports_missing_date} reports missing report date")
        
        if issues:
            print("⚠️ Data Integrity Issues Found:")
            for issue in issues:
                print(f"    {issue}")
        else:
            print("✅ No data integrity issues found!")
            
        # Check for duplicate files
        duplicate_files = db.execute(text("""
            SELECT file_path, COUNT(*) as count 
            FROM reports 
            GROUP BY file_path 
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicate_files:
            print(f"\n📄 Duplicate Files Found:")
            for row in duplicate_files:
                print(f"    {row[0]}: {row[1]} copies")
        else:
            print(f"\n✅ No duplicate files found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

def show_all_tables():
    """Show all tables in the database and their structure"""
    print("🗄️ DATABASE TABLES INSPECTOR")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get database inspector
        inspector = inspect(db.bind)
        
        # Get all table names
        table_names = inspector.get_table_names()
        print(f"📊 Found {len(table_names)} tables in database:")
        
        for table_name in table_names:
            print(f"\n📋 TABLE: {table_name}")
            print("-" * 40)
            
            # Get column information
            columns = inspector.get_columns(table_name)
            print("📝 COLUMNS:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                print(f"    {col['name']}: {col['type']} {nullable}{default}")
            
            # Get row count
            result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"📊 ROWS: {result}")
            
            # Show primary keys
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint['constrained_columns']:
                print(f"🔑 PRIMARY KEY: {', '.join(pk_constraint['constrained_columns'])}")
            
            # Show foreign keys
            fk_constraints = inspector.get_foreign_keys(table_name)
            if fk_constraints:
                print("🔗 FOREIGN KEYS:")
                for fk in fk_constraints:
                    print(f"    {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error inspecting tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def show_raw_table_data(table_name=None):
    """Show raw data from all tables or a specific table"""
    print("🗃️ RAW DATABASE CONTENT")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get database inspector
        inspector = inspect(db.bind)
        table_names = inspector.get_table_names()
        
        if table_name:
            if table_name not in table_names:
                print(f"❌ Table '{table_name}' not found!")
                print(f"Available tables: {', '.join(table_names)}")
                return
            tables_to_show = [table_name]
        else:
            tables_to_show = table_names
        
        for table in tables_to_show:
            print(f"\n📋 TABLE: {table}")
            print("=" * 50)
            
            # Get all data from table
            result = db.execute(text(f"SELECT * FROM {table}")).fetchall()
            
            if not result:
                print("📝 (No data in this table)")
                continue
            
            # Get column names
            columns = [col['name'] for col in inspector.get_columns(table)]
            
            # Print header
            print("📊 RAW DATA:")
            print("-" * 80)
            
            # Print column headers
            header = " | ".join(f"{col:15}" for col in columns)
            print(header)
            print("-" * len(header))
            
            # Print each row
            for i, row in enumerate(result, 1):
                row_data = []
                for j, value in enumerate(row):
                    if value is None:
                        display_value = "NULL"
                    elif isinstance(value, str) and len(value) > 50:
                        display_value = value[:47] + "..."
                    elif isinstance(value, datetime):
                        display_value = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        display_value = str(value)
                    row_data.append(f"{display_value:15}")
                
                print(f"#{i:3} | " + " | ".join(row_data))
            
            print(f"\n📊 Total rows: {len(result)}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error showing table data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def show_table_full_content(table_name):
    """Show complete content of a specific table with full text"""
    print(f"📋 COMPLETE TABLE CONTENT: {table_name}")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Get database inspector
        inspector = inspect(db.bind)
        
        if table_name not in inspector.get_table_names():
            print(f"❌ Table '{table_name}' not found!")
            return
        
        # Get all data from table
        result = db.execute(text(f"SELECT * FROM {table_name}")).fetchall()
        
        if not result:
            print("📝 (No data in this table)")
            return
        
        # Get column names
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        print(f"📊 Found {len(result)} rows with {len(columns)} columns")
        print("-" * 80)
        
        # Print each row with full content
        for i, row in enumerate(result, 1):
            print(f"\n🔢 ROW #{i}")
            print("-" * 40)
            
            for col_name, value in zip(columns, row):
                if value is None:
                    display_value = "NULL"
                elif isinstance(value, datetime):
                    display_value = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, str):
                    # Show full text content
                    if len(value) > 100:
                        display_value = f"{value}\n    (Length: {len(value)} characters)"
                    else:
                        display_value = value
                else:
                    display_value = str(value)
                
                print(f"  {col_name}: {display_value}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error showing table content: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def execute_custom_sql(sql_query):
    """Execute a custom SQL query"""
    print(f"🔍 EXECUTING SQL QUERY")
    print("=" * 50)
    print(f"Query: {sql_query}")
    print("-" * 50)
    
    db = SessionLocal()
    try:
        result = db.execute(text(sql_query)).fetchall()
        
        if not result:
            print("📝 No results returned")
            return
        
        # Print results
        for i, row in enumerate(result, 1):
            print(f"Row {i}: {dict(row._mapping) if hasattr(row, '_mapping') else row}")
            
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--patient" and len(sys.argv) > 2:
            view_specific_patient(sys.argv[2])
        elif sys.argv[1] == "--integrity":
            check_data_integrity()
        elif sys.argv[1] == "--tables":
            show_all_tables()
        elif sys.argv[1] == "--raw" and len(sys.argv) > 2:
            show_raw_table_data(sys.argv[2])
        elif sys.argv[1] == "--full" and len(sys.argv) > 2:
            show_table_full_content(sys.argv[2])
        else:
            print("Usage:")
            print("  python inspect_database.py                    # View all reports")
            print("  python inspect_database.py --patient CF123    # View specific patient")
            print("  python inspect_database.py --integrity        # Check data integrity")
            print("  python inspect_database.py --tables           # Show all tables and structure")
            print("  python inspect_database.py --raw TABLE_NAME   # Show raw data from a table")
            print("  python inspect_database.py --full TABLE_NAME  # Show complete content of a table")
    else:
        view_all_reports()
