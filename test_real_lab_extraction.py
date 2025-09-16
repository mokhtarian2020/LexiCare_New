#!/usr/bin/env python3
"""
Test extraction of real laboratory values from the PDFs
"""

import sys
import re
sys.path.append('backend')

from core.pdf_parser import extract_metadata

def test_real_lab_extraction():
    """Test laboratory value extraction with the actual PDF data"""
    
    pdf_files = [
        "1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf",  # Urine analysis
        "1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf"   # Blood chemistry & hematology
    ]
    
    print("🧪 Testing Real Laboratory Value Extraction")
    print("=" * 60)
    
    for pdf_file in pdf_files:
        print(f"\n📄 Testing: {pdf_file}")
        print("-" * 50)
        
        try:
            # Read and extract from PDF
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            metadata = extract_metadata(pdf_bytes)
            
            print("✅ Basic Info:")
            print(f"  Patient: {metadata.get('patient_name', 'Not found')}")
            print(f"  Birth Date: {metadata.get('birth_date', 'Not found')}")
            print(f"  Report Date: {metadata.get('report_date', 'Not found')}")
            print(f"  CF: {metadata.get('codice_fiscale', 'Not found')}")
            
            # Focus on laboratory values
            lab_values = metadata.get('laboratory_values', {})
            print(f"\n🔬 Laboratory Values Extracted: {len(lab_values)} total")
            
            if lab_values:
                # Group by category for better analysis
                categories = {}
                for test_name, test_data in lab_values.items():
                    category = test_data.get('category', 'unknown')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append((test_name, test_data))
                
                for category, tests in categories.items():
                    print(f"\n  📊 {category.title()} ({len(tests)} tests):")
                    for test_name, test_data in tests:
                        value = test_data['value']
                        unit = test_data['unit']
                        reference = test_data['reference']
                        abnormal = test_data['abnormal']
                        
                        line = f"    • {test_name}: {value}"
                        if unit:
                            line += f" {unit}"
                        if reference:
                            line += f" (ref: {reference})"
                        if abnormal:
                            line += " *ABNORMAL*"
                        
                        print(line)
            else:
                print("  ❌ No laboratory values extracted")
                
            # Show raw text for debugging
            raw_text = metadata.get('full_text', '')
            print(f"\n📝 Raw text length: {len(raw_text)} characters")
            
            # Look for specific patterns in the raw text
            print("\n🔍 Manual pattern search in raw text:")
            
            # Search for laboratory-like patterns
            lab_patterns = [
                r'(\w+)\s+([0-9]+[.,][0-9]+|\w+)\s*\*?\s*([a-zA-Z/%]+)?\s*([0-9].*)?',
                r'(Colore|Aspetto|Ph|Glucosio|Proteine|Emoglobina)\s+(.+?)(?:\n|$)',
                r'(WBC|RBC|HGB|HCT|PLT)\s+([0-9]+[.,][0-9]+)',
            ]
            
            for i, pattern in enumerate(lab_patterns):
                matches = re.findall(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    print(f"  Pattern {i+1} found {len(matches)} matches:")
                    for match in matches[:5]:  # Show first 5
                        print(f"    {match}")
                    if len(matches) > 5:
                        print(f"    ... and {len(matches) - 5} more")
                        
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🎯 Real Laboratory Extraction Test Completed!")

if __name__ == "__main__":
    test_real_lab_extraction()
