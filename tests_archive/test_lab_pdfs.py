#!/usr/bin/env python3
"""
Test the enhanced PDF parser with the actual laboratory PDFs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_metadata
import json

def test_lab_pdf_parsing():
    """Test the enhanced PDF parser with laboratory reports"""
    
    pdf_files = [
        "1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf",  # Urine analysis
        "1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf"   # Blood chemistry & hematology
    ]
    
    print("🧪 Testing Enhanced PDF Parser with Laboratory Reports")
    print("=" * 60)
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"❌ PDF file not found: {pdf_file}")
            continue
            
        print(f"\n📄 Testing: {pdf_file}")
        print("-" * 50)
        
        try:
            # Read the PDF file
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            # Extract metadata using our enhanced parser
            metadata = extract_metadata(pdf_bytes)
            
            print("✅ Extraction Results:")
            print(f"  Patient Name: {metadata.get('patient_name', 'Not found')}")
            print(f"  Birth Date: {metadata.get('birth_date', 'Not found')}")
            print(f"  Codice Fiscale: {metadata.get('codice_fiscale', 'Not found')}")
            print(f"  Report Date: {metadata.get('report_date', 'Not found')}")
            print(f"  Report Type: {metadata.get('report_type', 'Not found')}")
            
            # Show extracted dates
            extracted_dates = metadata.get('extracted_dates', {})
            if extracted_dates:
                print(f"  📅 Extracted Dates:")
                for date_type, date_value in extracted_dates.items():
                    print(f"    {date_type}: {date_value}")
            
            # Show laboratory values
            lab_values = metadata.get('laboratory_values', {})
            if lab_values:
                print(f"  🔬 Laboratory Values ({len(lab_values)} found):")
                
                # Group by type for better display
                hematology_tests = []
                chemistry_tests = []
                urine_tests = []
                
                for test_name, test_data in lab_values.items():
                    test_info = f"{test_name}: {test_data['value']}"
                    if test_data['unit']:
                        test_info += f" {test_data['unit']}"
                    if test_data['reference']:
                        test_info += f" (ref: {test_data['reference']})"
                    if test_data['abnormal']:
                        test_info += " *"
                    
                    # Categorize tests
                    if any(term in test_name.upper() for term in ['WBC', 'RBC', 'HGB', 'HCT', 'PLT', 'NEU', 'LYN', 'MON', 'EOS', 'BAS']):
                        hematology_tests.append(test_info)
                    elif any(term in test_name.upper() for term in ['GLUCOSIO', 'CREATININA', 'UREA', 'SODIO', 'POTASSIO', 'CALCIO', 'ALT', 'AST', 'BILIRUBINA']):
                        chemistry_tests.append(test_info)
                    elif any(term in test_name.upper() for term in ['COLORE', 'ASPETTO', 'PH', 'PROTEINE', 'EMOGLOBINA', 'GLUCOSIO', 'PESO']):
                        urine_tests.append(test_info)
                    else:
                        chemistry_tests.append(test_info)
                
                # Display categorized results
                if hematology_tests:
                    print(f"    🩸 Hematology ({len(hematology_tests)} tests):")
                    for test in hematology_tests[:5]:  # Show first 5
                        print(f"      • {test}")
                    if len(hematology_tests) > 5:
                        print(f"      ... and {len(hematology_tests) - 5} more")
                
                if chemistry_tests:
                    print(f"    ⚗️  Chemistry ({len(chemistry_tests)} tests):")
                    for test in chemistry_tests[:5]:  # Show first 5
                        print(f"      • {test}")
                    if len(chemistry_tests) > 5:
                        print(f"      ... and {len(chemistry_tests) - 5} more")
                
                if urine_tests:
                    print(f"    💧 Urinalysis ({len(urine_tests)} tests):")
                    for test in urine_tests[:5]:  # Show first 5
                        print(f"      • {test}")
                    if len(urine_tests) > 5:
                        print(f"      ... and {len(urine_tests) - 5} more")
            else:
                print("  🔬 No laboratory values extracted")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🎯 Laboratory PDF Testing Completed!")

if __name__ == "__main__":
    test_lab_pdf_parsing()
