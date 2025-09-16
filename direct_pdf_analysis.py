#!/usr/bin/env python3
"""
Direct PDF text extraction to examine real laboratory data
"""

import fitz  # PyMuPDF
import re

def extract_and_analyze_pdfs():
    """Extract raw text from PDFs and analyze for laboratory values"""
    
    pdf_files = [
        "1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf",  # Urine analysis
        "1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf"   # Blood chemistry & hematology
    ]
    
    for pdf_file in pdf_files:
        print(f"\n{'='*80}")
        print(f"📄 ANALYZING: {pdf_file}")
        print(f"{'='*80}")
        
        try:
            # Open PDF directly with PyMuPDF
            doc = fitz.open(pdf_file)
            
            full_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += text
            
            doc.close()
            
            print("🔍 RAW EXTRACTED TEXT:")
            print("-" * 60)
            print(full_text)
            print("-" * 60)
            
            # Analyze line by line for potential lab values
            lines = full_text.split('\n')
            print(f"\n📋 LINE-BY-LINE ANALYSIS ({len(lines)} lines):")
            print("-" * 60)
            
            potential_lab_lines = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                print(f"{i:3d}: '{line}'")
                
                # Look for patterns that might be laboratory values
                # Numbers with units, test names with values, etc.
                if (re.search(r'\b\d+[.,]\d+\b', line) or  # Decimal numbers
                    re.search(r'\b\d+\s*[a-zA-Z%/³µ]+\b', line) or  # Numbers with units
                    re.search(r'(mg|dl|g|l|mEq|mmol|µg|ng|pg|UI|IU|%)', line, re.I) or  # Common units
                    re.search(r'(WBC|RBC|HGB|HCT|PLT|NEU|LYN|MON|EOS)', line, re.I) or  # Hematology
                    re.search(r'(GLUCOSIO|CREATININA|UREA|SODIO|POTASSIO)', line, re.I) or  # Chemistry
                    re.search(r'(COLORE|ASPETTO|PH|PROTEINE)', line, re.I)):  # Urinalysis
                    potential_lab_lines.append((i, line))
            
            if potential_lab_lines:
                print(f"\n🔬 POTENTIAL LABORATORY VALUES ({len(potential_lab_lines)} found):")
                print("-" * 60)
                for line_num, line in potential_lab_lines:
                    print(f"Line {line_num:3d}: {line}")
            else:
                print("\n❌ NO POTENTIAL LABORATORY VALUES FOUND")
            
            # Look for specific patterns in the entire text
            print(f"\n🎯 SPECIFIC PATTERN SEARCH:")
            print("-" * 60)
            
            # Search for common Italian lab test patterns
            patterns = {
                'Hematology Values': r'(WBC|RBC|HGB|HCT|MCV|MCH|MCHC|PLT|NEU|LYN|MON|EOS|BAS)\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*([a-zA-Z/%³µ²]*)',
                'Chemistry Values': r'(GLUCOSIO|CREATININA|UREA|AZOTEMIA|SODIO|POTASSIO|CALCIO|ALBUMINA|BILIRUBINA)\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*([a-zA-Z/%]*)',
                'Urinalysis Values': r'(Colore|Aspetto|Ph|Peso\s*Specifico|Proteine|Glucosio|Sangue|Emoglobina)\s*[:=]?\s*([A-Za-z0-9]+[.,]?[0-9]*)\s*([a-zA-Z/%]*)',
                'General Lab Pattern': r'([A-Z][A-Za-z\s]{3,20})\s+([0-9]+[.,]?[0-9]*)\s*\*?\s*([a-zA-Z%/³µ²]+)',
                'Italian Units': r'([A-Za-z\s]+)\s+([0-9]+[.,]?[0-9]*)\s*(mg/dl|g/l|mEq/l|mmol/l|µg/l|ng/ml|pg/ml|UI/l|%|/µl|K/µl)',
            }
            
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    print(f"\n{pattern_name}:")
                    for match in matches[:10]:  # Show first 10 matches
                        print(f"  • {' | '.join(match)}")
                    if len(matches) > 10:
                        print(f"  ... and {len(matches) - 10} more")
                else:
                    print(f"\n{pattern_name}: No matches found")
            
            print("\n" + "="*80)
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    extract_and_analyze_pdfs()
