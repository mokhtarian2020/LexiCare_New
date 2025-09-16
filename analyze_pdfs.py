#!/usr/bin/env python3
"""
Script to analyze the PDF files in the repository
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_text_from_pdf, extract_metadata
import fitz

def analyze_pdf(filename):
    """Analyze a PDF file and extract all its content"""
    print(f"\n{'='*60}")
    print(f"ANALYZING PDF: {filename}")
    print(f"{'='*60}")
    
    try:
        # Read the PDF file
        with open(filename, 'rb') as f:
            pdf_bytes = f.read()
        
        # Extract text using PyMuPDF directly
        doc = fitz.open(filename)
        raw_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            raw_text += f"\n--- PAGE {page_num + 1} ---\n"
            raw_text += page_text
        doc.close()
        
        print(f"📄 Raw text content ({len(raw_text)} characters):")
        print("-" * 40)
        print(raw_text)
        print("-" * 40)
        
        # Try to extract metadata using our parser
        print("\n🔍 Attempting metadata extraction:")
        try:
            metadata = extract_metadata(pdf_bytes)
            print("✅ Metadata extraction results:")
            for key, value in metadata.items():
                if key != 'full_text':  # Skip full text to avoid repetition
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"❌ Error in metadata extraction: {str(e)}")
            
        return raw_text
        
    except Exception as e:
        print(f"❌ Error reading PDF {filename}: {str(e)}")
        return None

def main():
    """Main function to analyze both PDFs"""
    pdf_files = [
        "1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf",
        "1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf"
    ]
    
    extracted_texts = []
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            text = analyze_pdf(pdf_file)
            if text:
                extracted_texts.append((pdf_file, text))
        else:
            print(f"❌ PDF file not found: {pdf_file}")
    
    # Analyze patterns in the extracted texts
    print(f"\n{'='*60}")
    print("PATTERN ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    for filename, text in extracted_texts:
        print(f"\n📋 Analysis for {filename}:")
        
        # Look for common Italian laboratory patterns
        patterns_to_check = {
            "Patient Name": [
                r"(?:Paziente|Nome)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*)",
                r"Sig\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*)",
                r"(?:Intestato a|Per)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*)"
            ],
            "Birth Date": [
                r"(?:D\.?\s*Nasc\.?|Data di nascita|Nato il|Nata il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:DN|d\.n\.)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
            ],
            "Codice Fiscale": [
                r"(?:C(?:odice)?\s*F(?:iscale)?|CF|C\.F\.)[\s:.-]*([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])",
                r"([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])"
            ],
            "Exam Date": [
                r"(?:Data|Data esame|Data referto)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Eseguito il|Effettuato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Prelievo|Prelievo del)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
            ],
            "Laboratory Values": [
                r"([A-Za-z\s]+)[\s:.-]*([0-9]+\.?[0-9]*)\s*([a-zA-Z/]+)?",
                r"([A-Z][A-Za-z\s]+)[\s:.-]*([0-9]+,?[0-9]*)\s*(mg/dl|g/l|mmol/l|%|\w+/\w+)",
                r"(Emocromo|Glicemia|Colesterolo|Trigliceridi|HDL|LDL|Creatinina|Azotemia|Transaminasi|ALT|AST|Bilirubina)[\s:.-]*([0-9]+[,.]?[0-9]*)"
            ]
        }
        
        for category, patterns in patterns_to_check.items():
            print(f"  {category}:")
            found_any = False
            for pattern in patterns:
                matches = re.findall(pattern, text, re.I)
                if matches:
                    found_any = True
                    print(f"    ✅ Pattern matched: {pattern[:50]}...")
                    for match in matches[:3]:  # Show first 3 matches
                        if isinstance(match, tuple):
                            print(f"      → {' | '.join(match)}")
                        else:
                            print(f"      → {match}")
                    if len(matches) > 3:
                        print(f"      ... and {len(matches) - 3} more matches")
            if not found_any:
                print(f"    ❌ No matches found")

if __name__ == "__main__":
    import re
    main()
