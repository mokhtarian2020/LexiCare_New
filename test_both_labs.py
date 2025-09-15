#!/usr/bin/env python3
"""
Test both PDFs with the new laboratory analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_metadata
from core.ai_engine import analyze_laboratory_report

def test_both_pdfs():
    """Test both laboratory PDFs"""
    
    pdfs = [
        ("1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf", "Urine Analysis"),
        ("1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf", "Blood Chemistry & Hematology")
    ]
    
    print("🧪 Testing Laboratory Analysis on Both PDFs")
    print("=" * 60)
    
    for pdf_file, description in pdfs:
        if not os.path.exists(pdf_file):
            print(f"❌ PDF file not found: {pdf_file}")
            continue
            
        print(f"\n📄 {description}")
        print(f"   File: {pdf_file}")
        print("-" * 40)
        
        try:
            # Extract metadata
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            metadata = extract_metadata(pdf_bytes)
            
            # Quick summary
            patient = metadata.get('patient_name', 'Not found')
            lab_values = metadata.get('laboratory_values', {})
            abnormal_count = sum(1 for test_data in lab_values.values() if test_data.get('abnormal', False))
            
            print(f"👤 Patient: {patient}")
            print(f"🔬 Lab values: {len(lab_values)} total, {abnormal_count} abnormal")
            
            # Show abnormal values
            if abnormal_count > 0:
                print("⚠️  Abnormal values:")
                for test_name, test_data in lab_values.items():
                    if test_data.get('abnormal', False):
                        value = test_data['value']
                        unit = test_data.get('unit', '')
                        reference = test_data.get('reference', '')
                        print(f"   • {test_name}: {value} {unit} (ref: {reference})")
            
            # Run AI analysis
            print(f"\n🤖 AI Laboratory Analysis:")
            try:
                analysis = analyze_laboratory_report(metadata)
                
                diagnosis = analysis.get('diagnosis', 'Not available')
                classification = analysis.get('classification', 'Not available')
                
                print(f"   📋 Diagnosis: {diagnosis}")
                print(f"   🎯 Classification: {classification}")
                
                if 'errore' in analysis:
                    print(f"   ⚠️ Error: {analysis['errore']}")
                    
            except Exception as analysis_error:
                print(f"   ❌ Analysis failed: {str(analysis_error)}")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
    
    print(f"\n{'='*60}")
    print("✅ Laboratory Analysis Test Complete!")

if __name__ == "__main__":
    test_both_pdfs()
