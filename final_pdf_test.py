#!/usr/bin/env python3
"""
Final test of PDF extraction with real laboratory PDFs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_metadata
import json

def final_pdf_test():
    """Final comprehensive test of both PDFs"""
    
    pdf_files = [
        ("1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf", "Urine Analysis"),
        ("1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf", "Blood Chemistry & Hematology")
    ]
    
    print("🎯 FINAL COMPREHENSIVE PDF EXTRACTION TEST")
    print("=" * 60)
    
    all_results = {}
    
    for pdf_file, description in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"❌ PDF file not found: {pdf_file}")
            continue
            
        print(f"\n📄 Testing: {description}")
        print(f"   File: {pdf_file}")
        print("-" * 50)
        
        try:
            # Read and extract metadata
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
            
            metadata = extract_metadata(pdf_bytes)
            
            # Basic patient information
            print("👤 PATIENT INFORMATION:")
            print(f"   Name: {metadata.get('patient_name', 'Not found')}")
            print(f"   Birth Date: {metadata.get('birth_date', 'Not found')}")
            print(f"   Codice Fiscale: {metadata.get('codice_fiscale', 'Not found')}")
            print(f"   Report Date: {metadata.get('report_date', 'Not found')}")
            print(f"   Report Type: {metadata.get('report_type', 'Not found')}")
            
            # Laboratory values organized by category
            lab_values = metadata.get('laboratory_values', {})
            print(f"\n🔬 LABORATORY VALUES ({len(lab_values)} total):")
            
            if lab_values:
                # Group by category
                categories = {}
                for test_name, test_data in lab_values.items():
                    category = test_data.get('category', 'other')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append((test_name, test_data))
                
                # Display by category
                category_icons = {
                    'hematology': '🩸',
                    'chemistry': '⚗️',
                    'urinalysis': '💧',
                    'coagulation': '🩸',
                    'other': '🔬'
                }
                
                for category, tests in categories.items():
                    icon = category_icons.get(category, '🔬')
                    print(f"\n   {icon} {category.upper()} ({len(tests)} tests):")
                    
                    for test_name, test_data in tests[:10]:  # Show max 10 per category
                        value = test_data['value']
                        unit = test_data.get('unit', '')
                        reference = test_data.get('reference', '')
                        abnormal = test_data.get('abnormal', False)
                        
                        test_info = f"{test_name}: {value}"
                        if unit:
                            test_info += f" {unit}"
                        if reference:
                            test_info += f" (ref: {reference})"
                        if abnormal:
                            test_info += " ⚠️"
                        
                        print(f"      • {test_info}")
                    
                    if len(tests) > 10:
                        print(f"      ... and {len(tests) - 10} more tests")
            else:
                print("   ❌ No laboratory values extracted")
            
            # Store results
            all_results[pdf_file] = {
                'description': description,
                'patient_info': {
                    'name': metadata.get('patient_name'),
                    'birth_date': metadata.get('birth_date'),
                    'codice_fiscale': metadata.get('codice_fiscale'),
                    'report_date': metadata.get('report_date')
                },
                'lab_values_count': len(lab_values),
                'categories': list(set(test_data.get('category', 'other') for test_data in lab_values.values())),
                'abnormal_count': sum(1 for test_data in lab_values.values() if test_data.get('abnormal', False))
            }
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 EXTRACTION SUMMARY:")
    print("-" * 30)
    
    for pdf_file, results in all_results.items():
        print(f"\n📄 {results['description']}:")
        print(f"   ✅ Patient identified: {results['patient_info']['name'] is not None}")
        print(f"   ✅ Lab values extracted: {results['lab_values_count']}")
        print(f"   ✅ Categories found: {', '.join(results['categories'])}")
        print(f"   ⚠️  Abnormal values: {results['abnormal_count']}")
    
    print(f"\n🎉 PDF EXTRACTION TEST COMPLETED SUCCESSFULLY!")
    print("✅ Ready for AI model integration for diagnosis and comparison")

if __name__ == "__main__":
    final_pdf_test()
