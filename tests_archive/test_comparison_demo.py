#!/usr/bin/env python3
"""
Test script to demonstrate comparison functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.pdf_parser import extract_metadata
from backend.core.comparator import compare_with_previous_report_by_title, compare_with_latest_report_by_title_only
from backend.db.session import SessionLocal
from backend.db.models import Report
from backend.db import crud
import json

def test_comparison_workflow():
    """Test the complete comparison workflow"""
    
    print("🧪 Testing LexiCare Comparison Functionality")
    print("=" * 60)
    
    # Get database session
    db = SessionLocal()
    
    # Test files
    pdf_files = [
        "/home/amir/Documents/amir/LexiCare/1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf",
        "/home/amir/Documents/amir/LexiCare/1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf"
    ]
    
    for i, pdf_path in enumerate(pdf_files):
        print(f"\n📄 Testing PDF {i+1}: {os.path.basename(pdf_path)}")
        print("-" * 50)
        
        try:
            # Read and extract metadata
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            meta = extract_metadata(pdf_bytes)
            
            # Display extracted info
            print(f"✅ Patient Name: {meta.get('patient_name', 'Not found')}")
            print(f"✅ Codice Fiscale: {meta.get('codice_fiscale', 'Not found')}")
            print(f"✅ Report Type: {meta.get('report_type', 'Not found')}")
            print(f"✅ Report Date: {meta.get('report_date', 'Not found')}")
            print(f"✅ Lab Values: {len(meta.get('laboratory_values', {}))} values found")
            
            # Test comparison scenarios
            cf = meta.get('codice_fiscale')
            report_type = meta.get('report_type')
            full_text = meta.get('full_text', '')
            
            if cf and report_type:
                print(f"\n🔍 Testing comparison for CF: {cf}, Type: {report_type}")
                
                # Check if we have previous reports for this patient and type
                previous_reports = crud.get_patient_reports(db, cf, report_type)
                print(f"📊 Found {len(previous_reports)} existing reports for this patient/type")
                
                # Test comparison with previous report
                comparison = compare_with_previous_report_by_title(db, cf, report_type, full_text)
                print(f"🔄 Comparison Result:")
                print(f"   Status: {comparison.get('status', 'Unknown')}")
                print(f"   Explanation: {comparison.get('explanation', 'No explanation')}")
                
            else:
                print(f"\n⚠️ Missing CF or report type - testing title-only comparison")
                if report_type:
                    comparison = compare_with_latest_report_by_title_only(db, report_type, full_text)
                    print(f"🔄 Title-only Comparison Result:")
                    print(f"   Status: {comparison.get('status', 'Unknown')}")
                    print(f"   Explanation: {comparison.get('explanation', 'No explanation')}")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Show database state
    print(f"\n📋 Current Database State:")
    print("-" * 30)
    
    try:
        all_reports = db.query(Report).all()
        print(f"Total reports in database: {len(all_reports)}")
        
        for report in all_reports[:5]:  # Show first 5
            print(f"  - ID: {report.id}, CF: {report.patient_cf}, Type: {report.report_type}, Date: {report.report_date}")
            
        if len(all_reports) > 5:
            print(f"  ... and {len(all_reports) - 5} more reports")
            
    except Exception as e:
        print(f"❌ Error querying database: {str(e)}")
    
    print(f"\n✅ Comparison test completed!")

if __name__ == "__main__":
    test_comparison_workflow()
