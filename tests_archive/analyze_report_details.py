#!/usr/bin/env python3
"""
Detailed Report Analysis Script
Shows exactly what gets extracted from a PDF and how AI generates diagnosis
"""

import sys
import os
from pathlib import Path

# Change to backend directory for imports to work
script_dir = Path(__file__).parent
backend_dir = script_dir / "backend"
original_cwd = os.getcwd()

# Temporarily change to backend directory
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

try:
    from core.pdf_parser import extract_metadata
    from core.ai_engine import analyze_text_with_medgemma
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def analyze_report_extraction(pdf_path):
    """Show detailed extraction and AI processing for a report"""
    
    print("🔍 DETAILED REPORT ANALYSIS")
    print("=" * 50)
    print(f"📄 Analyzing: {pdf_path}")
    
    # Step 1: Extract text and metadata
    print("\n📄 STEP 1: PDF TEXT EXTRACTION")
    print("-" * 30)
    
    try:
        # Read PDF file as bytes
        with open(pdf_path, 'rb') as f:
            file_bytes = f.read()
        
        print(f"📁 File size: {len(file_bytes)} bytes")
        
        # Extract metadata using bytes
        metadata = extract_metadata(file_bytes)
        
        print(f"📋 Extracted Metadata:")
        for key, value in metadata.items():
            if key == 'full_text':
                print(f"  {key}: {len(str(value))} characters")
                print(f"    Preview: {str(value)[:200]}...")
            else:
                print(f"  {key}: {value}")
                
        full_text = metadata.get('full_text', '')
        report_type = metadata.get('report_type', 'Unknown')
        
    except Exception as e:
        print(f"❌ Error extracting metadata: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    
    # Step 2: Show complete extracted text
    print(f"\n📝 STEP 2: COMPLETE EXTRACTED TEXT")
    print("-" * 40)
    print(f"Report Type Detected: {report_type}")
    print(f"Full Text Length: {len(full_text)} characters")
    print(f"\n🔤 RAW TEXT SENT TO AI:")
    print("'" + "="*60)
    print(full_text)
    print("="*60 + "'")
    
    # Step 3: Extract laboratory values (if applicable)
    print(f"\n🔬 STEP 3: LABORATORY VALUES EXTRACTION")
    print("-" * 40)
    
    # Extract laboratory values using regex patterns
    import re
    
    lab_patterns = [
        (r'Proteine.*?([0-9,\.]+).*?mg/dl', 'Proteine'),
        (r'Glucosio.*?([0-9,\.]+).*?mg/dl', 'Glucosio'),
        (r'Creatinina.*?([0-9,\.]+).*?mg/dl', 'Creatinina'),
        (r'Emoglobina.*?([0-9,\.]+).*?mg/dl', 'Emoglobina'),
        (r'Urea.*?([0-9,\.]+).*?mg/dl', 'Urea'),
        (r'pH.*?([0-9,\.]+)', 'pH'),
        (r'Colesterolo.*?([0-9,\.]+)', 'Colesterolo'),
        (r'Trigliceridi.*?([0-9,\.]+)', 'Trigliceridi'),
        # More flexible patterns
        (r'Proteine[^\n]*?([0-9,\.]+)', 'Proteine_alt'),
        (r'Glucosio[^\n]*?([0-9,\.]+)', 'Glucosio_alt'),
    ]
    
    extracted_values = {}
    for pattern, param_name in lab_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            extracted_values[param_name] = matches[0].replace(',', '.')
            print(f"  ✅ {param_name}: {extracted_values[param_name]}")
    
    if not extracted_values:
        print("  ⚠️ No laboratory values found with standard patterns")
        
        # Try to find any numerical values
        all_numbers = re.findall(r'([0-9,\.]+)', full_text)
        print(f"  📊 All numerical values found: {all_numbers[:10]}...")
    
    # Step 4: Show what gets passed to AI
    print(f"\n🤖 STEP 4: AI ANALYSIS PROCESS")
    print("-" * 40)
    
    print(f"Input to AI Model:")
    print(f"  • Report Type: {report_type}")
    print(f"  • Text Length: {len(full_text)} chars")
    print(f"  • Key Values: {len(extracted_values)} parameters")
    
    # Step 5: Perform AI analysis
    print(f"\n🧠 STEP 5: AI DIAGNOSIS GENERATION")
    print("-" * 40)
    
    try:
        print("📡 Calling AI model (MedGemma)...")
        ai_result = analyze_text_with_medgemma(full_text)
        
        print(f"🎯 AI Analysis Result:")
        if isinstance(ai_result, dict):
            for key, value in ai_result.items():
                print(f"  • {key}: {value}")
        else:
            print(f"  • Result: {ai_result}")
            
        # Show diagnosis basis
        print(f"\n📋 DIAGNOSIS BASIS:")
        print(f"The AI diagnosis is based on:")
        print(f"  1. Report type identification: {report_type}")
        print(f"  2. Extracted numerical values: {list(extracted_values.keys())}")
        print(f"  3. Text pattern analysis of the complete report")
        print(f"  4. Medical knowledge from MedGemma model")
        print(f"  5. Laboratory values with abnormal markers (*)")
        
        # Show detailed lab analysis
        if 'laboratory_values' in metadata:
            print(f"\n🔬 DETAILED LABORATORY ANALYSIS:")
            lab_values = metadata['laboratory_values']
            abnormal_count = 0
            for param, details in lab_values.items():
                status = "⚠️ ABNORMAL" if details.get('abnormal') else "✅ NORMAL"
                if details.get('abnormal'):
                    abnormal_count += 1
                print(f"  • {param}: {details['value']} {details.get('unit', '')} ({details.get('reference', 'N/A')}) - {status}")
            
            print(f"\n📊 ABNORMAL VALUES: {abnormal_count}/{len(lab_values)} parameters")
        
    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")
        import traceback
        traceback.print_exc()
        print(f"🔄 Showing fallback diagnosis logic...")
        
        # Show fallback diagnosis
        fallback_diagnosis = "Analisi non completata"
        if extracted_values:
            fallback_diagnosis = f"Referto con {len(extracted_values)} parametri misurati"
        
        print(f"  Fallback Diagnosis: {fallback_diagnosis}")
    
    # Step 6: Summary
    print(f"\n📊 EXTRACTION SUMMARY")
    print("-" * 40)
    print(f"✅ Text Extraction: {len(full_text)} characters")
    print(f"✅ Report Type: {report_type}")
    print(f"✅ Lab Values: {len(extracted_values)} parameters")
    print(f"✅ AI Processing: {'Success' if 'ai_result' in locals() else 'Failed'}")
    
    return metadata, extracted_values

if __name__ == "__main__":
    pdf_path = "/home/amir/Documents/amir/LexiCare_new/report_2024_02_01.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        exit(1)
    
    analyze_report_extraction(pdf_path)
