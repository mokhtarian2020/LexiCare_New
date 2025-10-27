#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.pdf_parser import extract_metadata

def test_pdf_extraction():
    print("Testing PDF extraction with updated patterns...")
    print("=" * 60)
    
    # Test first PDF
    print('📄 Testing PDF 1 (Feb 2024):')
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            meta1 = extract_metadata(f.read())
            lab_values = meta1.get('laboratory_values', {})
            print(f'Laboratory values found: {len(lab_values)}')
            
            if lab_values:
                for name, data in lab_values.items():
                    abnormal_marker = " ⚠️" if data.get("abnormal") else ""
                    print(f'  ✅ {name}: {data["value"]} {data["unit"]} (ref: {data["reference"]}){abnormal_marker}')
            else:
                print('  ❌ No laboratory values extracted')
                
            # Check if Proteine was found specifically
            if 'Proteine' in lab_values:
                protein_val = lab_values['Proteine']['value']
                print(f'  🧪 Protein value: {protein_val} mg/dl')
            else:
                print('  ❌ Protein value not found')
                
    except Exception as e:
        print(f'  ❌ Error: {e}')
    
    print()
    
    # Test second PDF
    print('📄 Testing PDF 2 (May 2024):')
    try:
        with open('report_2024_05_01.pdf', 'rb') as f:
            meta2 = extract_metadata(f.read())
            lab_values = meta2.get('laboratory_values', {})
            print(f'Laboratory values found: {len(lab_values)}')
            
            if lab_values:
                for name, data in lab_values.items():
                    abnormal_marker = " ⚠️" if data.get("abnormal") else ""
                    print(f'  ✅ {name}: {data["value"]} {data["unit"]} (ref: {data["reference"]}){abnormal_marker}')
            else:
                print('  ❌ No laboratory values extracted')
                
            # Check if Proteine was found specifically
            if 'Proteine' in lab_values:
                protein_val = lab_values['Proteine']['value']
                print(f'  🧪 Protein value: {protein_val} mg/dl')
            else:
                print('  ❌ Protein value not found')
                
    except Exception as e:
        print(f'  ❌ Error: {e}')

if __name__ == "__main__":
    test_pdf_extraction()
