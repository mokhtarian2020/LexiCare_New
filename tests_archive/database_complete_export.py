#!/usr/bin/env python3
"""
Comprehensive Database Summary and Raw Data Export
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
    from sqlalchemy import text
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def export_all_data():
    """Export all database data to JSON for easy inspection"""
    print("📊 EXPORTING ALL DATABASE DATA")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Get all reports with all fields
        result = db.execute(text("""
            SELECT * FROM reports ORDER BY created_at
        """))
        
        reports = result.fetchall()
        column_names = list(result.keys())
        
        # Convert to list of dictionaries
        data = []
        for report in reports:
            report_dict = {}
            for col_name, value in zip(column_names, report):
                # Convert datetime and UUID to string for JSON serialization
                if hasattr(value, 'isoformat'):
                    report_dict[col_name] = value.isoformat()
                else:
                    report_dict[col_name] = str(value) if value is not None else None
            data.append(report_dict)
        
        # Export to JSON file
        export_file = script_dir / f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(data)} reports to: {export_file}")
        
        # Also create a human-readable summary
        summary_file = script_dir / f"database_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("LEXICARE DATABASE SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Reports: {len(data)}\n\n")
            
            for i, report in enumerate(data, 1):
                f.write(f"REPORT #{i}\n")
                f.write("-" * 30 + "\n")
                f.write(f"ID: {report['id']}\n")
                f.write(f"Patient: {report['patient_name']} (CF: {report['patient_cf']})\n")
                f.write(f"Type: {report['report_type']}\n")
                f.write(f"Category: {report.get('report_category', 'N/A')}\n")
                f.write(f"Date: {report['report_date']}\n")
                f.write(f"Created: {report['created_at']}\n")
                f.write(f"AI Diagnosis: {report['ai_diagnosis']}\n")
                f.write(f"AI Classification: {report['ai_classification']}\n")
                f.write(f"Doctor Diagnosis: {report.get('doctor_diagnosis', 'N/A')}\n")
                f.write(f"Doctor Classification: {report.get('doctor_classification', 'N/A')}\n")
                f.write(f"Doctor Comment: {report.get('doctor_comment', 'N/A')}\n")
                f.write(f"Comparison: {report.get('comparison_to_previous', 'N/A')}\n")
                f.write(f"Comparison Explanation: {report.get('comparison_explanation', 'N/A')[:200]}...\n")
                f.write(f"File Path: {report['file_path']}\n")
                f.write("\n" + "=" * 50 + "\n\n")
        
        print(f"✅ Created summary report: {summary_file}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def show_database_stats():
    """Show detailed database statistics"""
    print("\n📈 DATABASE STATISTICS")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        queries = [
            ("Total reports", "SELECT COUNT(*) FROM reports"),
            ("Reports by type", """
                SELECT report_type, COUNT(*) as count 
                FROM reports 
                GROUP BY report_type 
                ORDER BY count DESC
            """),
            ("Reports by category", """
                SELECT report_category, COUNT(*) as count 
                FROM reports 
                GROUP BY report_category 
                ORDER BY count DESC
            """),
            ("Reports with feedback", """
                SELECT COUNT(*) FROM reports 
                WHERE doctor_diagnosis IS NOT NULL 
                   OR doctor_classification IS NOT NULL 
                   OR doctor_comment IS NOT NULL
            """),
            ("Reports with comparison", """
                SELECT COUNT(*) FROM reports 
                WHERE comparison_to_previous IS NOT NULL
            """),
            ("AI classifications", """
                SELECT ai_classification, COUNT(*) as count 
                FROM reports 
                GROUP BY ai_classification 
                ORDER BY count DESC
            """),
            ("Doctor classifications", """
                SELECT doctor_classification, COUNT(*) as count 
                FROM reports 
                WHERE doctor_classification IS NOT NULL
                GROUP BY doctor_classification 
                ORDER BY count DESC
            """),
            ("Patients", """
                SELECT COUNT(DISTINCT patient_cf) as unique_patients,
                       COUNT(*) as total_reports,
                       COUNT(*) * 1.0 / COUNT(DISTINCT patient_cf) as avg_reports_per_patient
                FROM reports
            """)
        ]
        
        for title, query in queries:
            print(f"\n📊 {title}:")
            try:
                result = db.execute(text(query))
                rows = result.fetchall()
                
                if result.keys():
                    column_names = list(result.keys())
                    for row in rows:
                        if len(column_names) == 1:
                            print(f"  {row[0]}")
                        else:
                            row_dict = dict(zip(column_names, row))
                            print(f"  {row_dict}")
                else:
                    for row in rows:
                        print(f"  {row}")
                        
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_data_integrity():
    """Check for data integrity issues"""
    print("\n🔍 DATA INTEGRITY CHECK")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        checks = [
            ("Reports without patient CF", "SELECT COUNT(*) FROM reports WHERE patient_cf IS NULL OR patient_cf = ''"),
            ("Reports without report type", "SELECT COUNT(*) FROM reports WHERE report_type IS NULL OR report_type = ''"),
            ("Reports without AI diagnosis", "SELECT COUNT(*) FROM reports WHERE ai_diagnosis IS NULL OR ai_diagnosis = ''"),
            ("Duplicate reports (same patient, type, date)", """
                SELECT patient_cf, report_type, report_date, COUNT(*) as count
                FROM reports 
                GROUP BY patient_cf, report_type, report_date 
                HAVING COUNT(*) > 1
            """),
            ("Missing files", """
                SELECT id, file_path FROM reports 
                WHERE file_path IS NULL OR file_path = ''
            """)
        ]
        
        for title, query in checks:
            print(f"\n🔍 {title}:")
            try:
                result = db.execute(text(query))
                rows = result.fetchall()
                
                if not rows or (len(rows) == 1 and rows[0][0] == 0):
                    print("  ✅ No issues found")
                else:
                    print(f"  ⚠️  Found {len(rows)} issues:")
                    for row in rows:
                        print(f"    {row}")
                        
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🗄️ LEXICARE DATABASE COMPLETE INSPECTION & EXPORT")
    print("=" * 80)
    print(f"📅 Export time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Export all data
    data = export_all_data()
    
    # Show statistics
    show_database_stats()
    
    # Check data integrity
    check_data_integrity()
    
    print("\n✅ Database inspection and export complete!")
    
    if data:
        print(f"\n📋 SUMMARY:")
        print(f"  • Total reports: {len(data)}")
        print(f"  • Unique patients: {len(set(r['patient_cf'] for r in data))}")
        print(f"  • Report types: {len(set(r['report_type'] for r in data))}")
        print(f"  • Reports with feedback: {sum(1 for r in data if r.get('doctor_diagnosis'))}")
        print(f"  • Reports with comparison: {sum(1 for r in data if r.get('comparison_to_previous'))}")
