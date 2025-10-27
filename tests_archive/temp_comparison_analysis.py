#!/usr/bin/env python3
"""
TEMPORARY SCRIPT - Shows exactly what text gets passed to AI for comparison
This script will be deleted after analysis
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def show_comparison_texts():
    """Show exactly what text gets passed to AI for comparison"""
    
    print("🔍 EXACT TEXT PASSED TO AI FOR CONFRONTO")
    print("=" * 60)
    
    # Change to backend directory temporarily
    original_cwd = os.getcwd()
    os.chdir(backend_dir)
    
    try:
        from core.pdf_parser import extract_metadata
        
        # Analyze both reports
        report1_path = "/home/amir/Documents/amir/LexiCare_new/report_2024_02_01.pdf"
        report2_path = "/home/amir/Documents/amir/LexiCare_new/report_2024_05_01_modified.pdf"
        
        reports = []
        
        for i, pdf_path in enumerate([report1_path, report2_path], 1):
            print(f"\n📄 REPORT {i}: {os.path.basename(pdf_path)}")
            print("=" * 50)
            
            try:
                # Extract text exactly as the system does
                with open(pdf_path, 'rb') as f:
                    file_bytes = f.read()
                
                metadata = extract_metadata(file_bytes)
                full_text = metadata.get('full_text', '')
                report_date = metadata.get('report_date', 'Unknown')
                
                print(f"📅 Report Date: {report_date}")
                print(f"📊 Text Length: {len(full_text)} characters")
                
                print(f"\n🔤 EXACT TEXT SENT TO AI:")
                print("'" + "="*60)
                print(full_text)
                print("="*60 + "'")
                
                reports.append({
                    'file': os.path.basename(pdf_path),
                    'date': report_date,
                    'text': full_text,
                    'metadata': metadata
                })
                
            except Exception as e:
                print(f"❌ Error processing {pdf_path}: {e}")
        
        # Show comparison order
        if len(reports) == 2:
            print(f"\n🔄 COMPARISON PROCESS")
            print("=" * 60)
            
            # Determine chronological order based on dates
            print(f"📅 Date Analysis:")
            print(f"  Report 1: {reports[0]['date']}")
            print(f"  Report 2: {reports[1]['date']}")
            
            # Convert dates to compare
            from datetime import datetime
            
            try:
                date1 = datetime.strptime(reports[0]['date'], '%d/%m/%Y')
                date2 = datetime.strptime(reports[1]['date'], '%d/%m/%Y')
                
                if date1 < date2:
                    older_idx, newer_idx = 0, 1
                    print(f"  📊 Chronological Order: Report 1 (older) → Report 2 (newer)")
                else:
                    older_idx, newer_idx = 1, 0
                    print(f"  📊 Chronological Order: Report 2 (older) → Report 1 (newer)")
                
                older_report = reports[older_idx]
                newer_report = reports[newer_idx]
                
                print(f"\n🤖 AI COMPARISON INPUT:")
                print("=" * 60)
                
                print(f"📋 PREVIOUS REPORT TEXT (Older - {older_report['date']}):")
                print("'" + "-"*50)
                print(older_report['text'])
                print("-"*50 + "'")
                
                print(f"\n📋 CURRENT REPORT TEXT (Newer - {newer_report['date']}):")
                print("'" + "-"*50)
                print(newer_report['text'])
                print("-"*50 + "'")
                
                # Extract specific values that AI will compare
                print(f"\n🎯 KEY VALUES EXTRACTED FOR COMPARISON:")
                print("=" * 60)
                
                import re
                
                # Extract protein values
                older_protein = re.search(r'Proteine.*?([0-9,\.]+).*?mg/dl', older_report['text'], re.IGNORECASE)
                newer_protein = re.search(r'Proteine.*?([0-9,\.]+).*?mg/dl', newer_report['text'], re.IGNORECASE)
                
                if older_protein and newer_protein:
                    old_val = older_protein.group(1).replace(',', '.')
                    new_val = newer_protein.group(1).replace(',', '.')
                    print(f"🔬 Proteine:")
                    print(f"  Previous: {old_val} mg/dl")
                    print(f"  Current:  {new_val} mg/dl")
                    print(f"  Change:   {old_val} → {new_val}")
                
                # Extract other values
                patterns = {
                    'Emoglobina': r'Emoglobina.*?([0-9,\.]+).*?mg/dl',
                    'pH': r'pH.*?([0-9,\.]+)',
                    'Esterasi': r'Esterasi.*?([0-9,\.]+).*?Leu/ul'
                }
                
                for param, pattern in patterns.items():
                    older_match = re.search(pattern, older_report['text'], re.IGNORECASE)
                    newer_match = re.search(pattern, newer_report['text'], re.IGNORECASE)
                    
                    if older_match and newer_match:
                        old_val = older_match.group(1).replace(',', '.')
                        new_val = newer_match.group(1).replace(',', '.')
                        print(f"🔬 {param}:")
                        print(f"  Previous: {old_val}")
                        print(f"  Current:  {new_val}")
                        print(f"  Change:   {old_val} → {new_val}")
                
                print(f"\n💬 AI PROMPT STRUCTURE:")
                print("=" * 60)
                print("The AI receives a prompt like:")
                print("'" + "-"*40)
                print("Confronta questi due referti medici:")
                print("Referto precedente:")
                print(f"{older_report['text'][:100]}...")
                print("Referto attuale:")
                print(f"{newer_report['text'][:100]}...")
                print("Spiega i cambiamenti nei valori e se la situazione è migliorata/peggiorata.")
                print("-"*40 + "'")
                
            except Exception as e:
                print(f"❌ Error processing dates: {e}")
                print("Showing reports in upload order...")
    
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    show_comparison_texts()
