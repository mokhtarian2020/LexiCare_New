#!/usr/bin/env python3
"""
Debug script to examine the actual content of the PDFs
"""

import fitz  # PyMuPDF

def debug_pdf_content():
    """Examine the raw content of both PDFs to understand their structure"""
    
    pdf_files = [
        "1905282044015323ODM_5cee2e8773dbdb8e358ab670.pdf",  # Urine analysis
        "1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf"   # Blood chemistry & hematology
    ]
    
    for pdf_file in pdf_files:
        print(f"\n📄 Debugging: {pdf_file}")
        print("=" * 80)
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_file)
            
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            
            print("🔍 RAW PDF TEXT:")
            print("-" * 40)
            print(text)
            print("-" * 40)
            
            # Show line by line with numbers
            lines = text.split('\n')
            print(f"\n📋 LINE-BY-LINE ANALYSIS ({len(lines)} lines):")
            print("-" * 50)
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # Only show non-empty lines
                    print(f"{i:3d}: '{line}'")
            
            print("\n" + "=" * 80)
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_content()
