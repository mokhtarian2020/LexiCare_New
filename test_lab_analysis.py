#!/usr/bin/env python3
"""
Test the new laboratory analysis function
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_metadata
from core.ai_engine import analyze_laboratory_report

def test_lab_analysis():
    """Test the laboratory analysis function"""
    
    pdf_file = "1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf"  # Urine analysis
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return
        
    print("🧪 Testing Laboratory Analysis Function")
    print("=" * 50)
    
    try:
        # Extract metadata
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()
        
        metadata = extract_metadata(pdf_bytes)
        
        print(f"📄 PDF: {pdf_file}")
        print(f"👤 Patient: {metadata.get('patient_name', 'Not found')}")
        print(f"📅 Date: {metadata.get('report_date', 'Not found')}")
        
        lab_values = metadata.get('laboratory_values', {})
        print(f"🔬 Laboratory values found: {len(lab_values)}")
        
        if lab_values:
            print("\n📋 Key laboratory findings:")
            abnormal_count = 0
            for test_name, test_data in list(lab_values.items())[:5]:  # Show first 5
                value = test_data['value']
                unit = test_data.get('unit', '')
                abnormal = test_data.get('abnormal', False)
                if abnormal:
                    abnormal_count += 1
                
                status = " ⚠️" if abnormal else ""
                print(f"   • {test_name}: {value} {unit}{status}")
            
            if len(lab_values) > 5:
                print(f"   ... and {len(lab_values) - 5} more values")
            
            print(f"   Total abnormal values: {abnormal_count}")
            
            # Test the new analysis function
            print(f"\n🤖 Running AI Laboratory Analysis...")
            print("-" * 30)
            
            try:
                analysis = analyze_laboratory_report(metadata)
                
                print(f"✅ Analysis Results:")
                print(f"   Diagnosis: {analysis.get('diagnosis', 'Not available')}")
                print(f"   Classification: {analysis.get('classification', 'Not available')}")
                
                if 'errore' in analysis:
                    print(f"   ⚠️ Error: {analysis['errore']}")
                    
            except Exception as analysis_error:
                print(f"❌ Analysis failed: {str(analysis_error)}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ No laboratory values found - cannot perform analysis")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lab_analysis()
