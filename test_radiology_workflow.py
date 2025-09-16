#!/usr/bin/env python3
"""
Test the complete radiology PDF processing workflow.
"""

import sys
import os
sys.path.append('/home/amir/Documents/amir/LexiCare/backend')

from core.pdf_parser import extract_metadata
from core.ai_engine import analyze_laboratory_report
from core.comparator import compare_with_previous_reports
from db.session import SessionLocal
from db.models import Report
from db.crud import create_report, get_patient_reports

# Test the radiology PDF
pdf_path = "/home/amir/Documents/amir/LexiCare_documents/EXPORT_REF/209814_Non assegnato_REFERTO DI RADIOLOGIA.pdf"

print("🧪 TESTING COMPLETE RADIOLOGY WORKFLOW")
print("=" * 60)

# Read the PDF file
with open(pdf_path, 'rb') as f:
    file_bytes = f.read()

# Step 1: Extract metadata
print("1️⃣ Extracting metadata...")
metadata = extract_metadata(file_bytes)

print(f"   Patient: {metadata.get('patient_name')}")
print(f"   Type: {metadata.get('report_type')}")
print(f"   Date: {metadata.get('report_date')}")
print(f"   Lab values: {len(metadata.get('laboratory_values', {}))}")

# Step 2: AI Analysis
print("\n2️⃣ Running AI analysis...")
try:
    ai_analysis = analyze_laboratory_report(metadata)
    print(f"   AI Analysis: {ai_analysis.get('analysis', 'No analysis')[:100]}...")
    print(f"   Recommendations: {ai_analysis.get('recommendations', 'No recommendations')[:100]}...")
except Exception as e:
    print(f"   ❌ AI analysis failed: {e}")

# Step 3: Save to database
print("\n3️⃣ Saving to database...")
db = SessionLocal()
try:
    # Check for existing reports
    existing_reports = get_patient_reports(
        db, 
        metadata.get('codice_fiscale', 'Unknown'),
        metadata.get('report_type', 'Unknown')
    )
    
    print(f"   Found {len(existing_reports)} existing reports for this patient/type")
    
    # Save PDF file first
    pdf_filename = os.path.basename(pdf_path)
    saved_file_path = f"backend/storage/{pdf_filename}"
    
    # Copy the file to storage
    os.makedirs("backend/storage", exist_ok=True)
    import shutil
    shutil.copy2(pdf_path, saved_file_path)
    
    # Save the new report
    new_report = create_report(
        db=db,
        patient_cf=metadata.get('codice_fiscale', 'Unknown'),
        patient_name=metadata.get('patient_name', 'Unknown'),
        report_type=metadata.get('report_type', 'Unknown'),
        report_date=metadata.get('report_date'),
        file_path=saved_file_path,
        extracted_text=metadata.get('full_text', ''),
        ai_diagnosis=ai_analysis.get('analysis', 'No analysis') if 'ai_analysis' in locals() else 'No analysis',
        ai_classification=ai_analysis.get('classification', 'moderato') if 'ai_analysis' in locals() else 'moderato'
    )
    
    print(f"   ✅ Saved report with ID: {new_report.id}")
    
    # Step 4: Test comparison if there are existing reports
    if len(existing_reports) > 0:
        print("\n4️⃣ Testing comparison...")
        
        # Get the most recent previous report
        comparison_result = compare_with_previous_reports(
            db=db,
            patient_cf=metadata.get('codice_fiscale', ''),
            report_type=metadata.get('report_type', 'Unknown'),
            new_text=metadata.get('full_text', '')
        )
        
        print(f"   Comparison result: {comparison_result.get('comparison', 'No comparison')[:100]}...")
        print(f"   Clinical significance: {comparison_result.get('clinical_significance', 'No significance')}")
    else:
        print("\n4️⃣ No previous reports for comparison")
    
except Exception as e:
    print(f"   ❌ Database operation failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n🎉 Workflow test completed!")
