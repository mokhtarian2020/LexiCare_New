#!/usr/bin/env python3
"""
Test the comparison functionality with the two PDF files in the repository
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.pdf_parser import extract_metadata
from backend.core.comparator import compare_with_previous_report_by_title
from backend.db.session import SessionLocal
from backend.db.models import Report
from backend.db import crud
from datetime import datetime

def test_pdf_comparison():
    """Test comparison with the two PDF files"""
    
    print("🧪 Testing PDF Comparison - Protein Values 15 vs 45")
    print("=" * 60)
    
    # Your PDF files
    pdf_files = [
        "/home/amir/Documents/amir/LexiCare/report_2024_02_01.pdf",  # Should have proteine 15
        "/home/amir/Documents/amir/LexiCare/report_2024_05_01.pdf"   # Should have proteine 45
    ]
    
    db = SessionLocal()
    extracted_data = []
    
    print("📄 ANALYZING YOUR PDF FILES:")
    print("-" * 40)
    
    # First, extract metadata from both PDFs
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📋 PDF {i}: {os.path.basename(pdf_path)}")
        
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            continue
            
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            meta = extract_metadata(pdf_bytes)
            extracted_data.append({
                'path': pdf_path,
                'meta': meta,
                'bytes': pdf_bytes
            })
            
            print(f"   👤 Patient: {meta.get('patient_name', 'Not found')}")
            print(f"   🆔 CF: {meta.get('codice_fiscale', 'Not found')}")
            print(f"   🔬 Type: {meta.get('report_type', 'Not found')}")
            print(f"   📅 Date: {meta.get('report_date', 'Not found')}")
            print(f"   🧪 Lab Values: {len(meta.get('laboratory_values', {}))} found")
            
            # Show protein values specifically
            lab_values = meta.get('laboratory_values', {})
            protein_found = False
            for test_name, values in lab_values.items():
                if 'protein' in test_name.lower() or 'proteine' in test_name.lower():
                    print(f"   🟡 {test_name}: {values.get('value', 'N/A')} {values.get('unit', '')}")
                    protein_found = True
            
            if not protein_found:
                print("   ⚠️ No protein values found in lab results")
                # Check raw text for protein mentions
                full_text = meta.get('full_text', '')
                if 'protein' in full_text.lower() or 'proteine' in full_text.lower():
                    print("   💡 But protein mentioned in text - checking...")
                    # Find protein value in text
                    import re
                    protein_match = re.search(r'protein[ei].*?(\d+)', full_text, re.IGNORECASE)
                    if protein_match:
                        print(f"   🔍 Found protein value in text: {protein_match.group(1)}")
                        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    if len(extracted_data) != 2:
        print(f"\n❌ Could not extract data from both PDFs")
        return
    
    print(f"\n🔄 TESTING COMPARISON LOGIC:")
    print("-" * 40)
    
    # Check if they have same patient and report type
    data1, data2 = extracted_data[0], extracted_data[1]
    cf1 = data1['meta'].get('codice_fiscale')
    cf2 = data2['meta'].get('codice_fiscale') 
    type1 = data1['meta'].get('report_type')
    type2 = data2['meta'].get('report_type')
    
    print(f"📊 CF Match: {cf1} == {cf2} → {'✅' if cf1 == cf2 else '❌'}")
    print(f"📊 Type Match: '{type1}' == '{type2}' → {'✅' if type1 == type2 else '❌'}")
    
    if cf1 != cf2:
        print("⚠️ Different patients - comparison won't work")
        return
        
    if type1 != type2:
        print("⚠️ Different report types - comparison won't work")
        return
    
    # Simulate the upload process
    print(f"\n🔄 SIMULATING UPLOAD PROCESS:")
    print("-" * 40)
    
    # Clear any existing data for this patient
    if cf1:
        existing = crud.get_patient_reports(db, cf1)
        if existing:
            print(f"🗑️ Clearing {len(existing)} existing reports for testing...")
            for report in existing:
                db.delete(report)
            db.commit()
    
    # Upload first PDF (should have no comparison)
    print(f"\n1️⃣ UPLOADING FIRST PDF (proteine 15)...")
    try:
        report1 = crud.create_report(
            db=db,
            patient_cf=cf1,
            patient_name=data1['meta'].get('patient_name'),
            report_type=type1,
            report_date=datetime(2024, 2, 1),  # Earlier date
            file_path="test/report_2024_02_01.pdf",
            extracted_text=data1['meta'].get('full_text', ''),
            ai_diagnosis="Test diagnosis - proteine 15",
            ai_classification="lieve"
        )
        print(f"   ✅ Saved first report with ID: {report1.id}")
        
        # Test comparison (should be "nessun confronto disponibile")
        comparison1 = compare_with_previous_report_by_title(
            db, cf1, type1, data1['meta'].get('full_text', '')
        )
        print(f"   📊 Comparison: {comparison1.get('status', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return
    
    # Upload second PDF (should show comparison)
    print(f"\n2️⃣ UPLOADING SECOND PDF (proteine 45)...")
    try:
        report2 = crud.create_report(
            db=db,
            patient_cf=cf2,
            patient_name=data2['meta'].get('patient_name'),
            report_type=type2,
            report_date=datetime(2024, 5, 1),  # Later date
            file_path="test/report_2024_05_01.pdf", 
            extracted_text=data2['meta'].get('full_text', ''),
            ai_diagnosis="Test diagnosis - proteine 45",
            ai_classification="moderato"
        )
        print(f"   ✅ Saved second report with ID: {report2.id}")
        
        # Test comparison (should show "peggiorata")
        comparison2 = compare_with_previous_report_by_title(
            db, cf2, type2, data2['meta'].get('full_text', '')
        )
        print(f"   📊 Comparison: {comparison2.get('status', 'Unknown')}")
        print(f"   💬 Explanation: {comparison2.get('explanation', 'No explanation')}")
        
        if comparison2.get('status') == 'peggiorata':
            print("   🔴 ✅ COMPARISON WORKING! Status correctly shows worsening")
        elif comparison2.get('status') == 'errore':
            print("   ❌ AI comparison failed - checking why...")
            print(f"       Error: {comparison2.get('explanation', 'Unknown error')}")
        else:
            print(f"   ⚠️ Unexpected status: {comparison2.get('status')}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_pdf_comparison()
