#!/usr/bin/env python3
"""
Test the improved exam title extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_metadata

def test_exam_title_extraction():
    """Test the improved exam title extraction on both PDFs"""
    
    pdfs = [
        ("1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf", "Should find: ESAME CHIMICO FISICO DELLE URINE"),
        ("1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf", "Should find: ESAME EMOCROMOCITOMETRICO")
    ]
    
    print("🔍 Testing Improved Exam Title Extraction")
    print("=" * 50)
    
    for pdf_file, expected in pdfs:
        if not os.path.exists(pdf_file):
            print(f"❌ PDF file not found: {pdf_file}")
            continue
            
        print(f"\n📄 Testing: {pdf_file}")
        print(f"   Expected: {expected}")
        print("-" * 40)
        
        try:
            # Extract metadata
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            metadata = extract_metadata(pdf_bytes)
            
            # Check the extracted report type
            report_type = metadata.get('report_type', 'Not found')
            patient_name = metadata.get('patient_name', 'Not found')
            
            print(f"✅ Results:")
            print(f"   Patient: {patient_name}")
            print(f"   Report Type: {report_type}")
            
            # Check if it found the right exam title
            if 'CHIMICO FISICO' in report_type.upper():
                print(f"   🎯 SUCCESS: Found specific urine exam title!")
            elif 'EMOCROMOCITOMETRICO' in report_type.upper():
                print(f"   🎯 SUCCESS: Found specific blood exam title!")
            elif report_type and report_type != 'sconosciuto' and 'Risultato Unita' not in report_type:
                print(f"   ✅ GOOD: Found meaningful title (not generic)")
            else:
                print(f"   ⚠️ ISSUE: Still getting generic or no title")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
    
    print(f"\n{'='*50}")
    print("🎯 Exam Title Extraction Test Complete!")

if __name__ == "__main__":
    test_exam_title_extraction()
