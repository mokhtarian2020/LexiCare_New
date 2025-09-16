#!/usr/bin/env python3
"""
Debug script to specifically analyze the radiology PDF extraction issues.
"""

import sys
import os
sys.path.append('/home/amir/Documents/amir/LexiCare/backend')

from core.pdf_parser import extract_metadata, extract_text_from_pdf
import re

# Test the radiology PDF
pdf_path = "/home/amir/Documents/amir/LexiCare_documents/EXPORT_REF/209814_Non assegnato_REFERTO DI RADIOLOGIA.pdf"

print("🔍 ANALYZING RADIOLOGY PDF EXTRACTION")
print("=" * 60)

# Read the PDF file
with open(pdf_path, 'rb') as f:
    file_bytes = f.read()

# Extract raw text
text, doc = extract_text_from_pdf(file_bytes)

print(f"📄 Raw text length: {len(text)} characters")
print("\n" + "=" * 60)
print("📝 FIRST 1000 CHARACTERS OF RAW TEXT:")
print("=" * 60)
print(text[:1000])
print("=" * 60)

# Look for the patient name specifically
print("\n🔍 SEARCHING FOR PATIENT NAME 'Palumbo Maria Grazia':")
print("=" * 60)

# Split text into lines for analysis
lines = text.splitlines()
for i, line in enumerate(lines[:30]):  # First 30 lines
    if 'palumbo' in line.lower() or 'maria' in line.lower() or 'grazia' in line.lower():
        print(f"Line {i+1}: '{line.strip()}'")

# Look for "Nome:" specifically
print("\n🔍 SEARCHING FOR 'Nome:' patterns:")
print("=" * 60)
for i, line in enumerate(lines[:50]):
    if 'nome' in line.lower():
        print(f"Line {i+1}: '{line.strip()}'")
        # Show next line too
        if i+1 < len(lines):
            print(f"Line {i+2}: '{lines[i+1].strip()}'")
        print("---")

# Look for exam type
print("\n🔍 SEARCHING FOR RADIOLOGY/EXAM TYPE:")
print("=" * 60)
for i, line in enumerate(lines[:50]):
    if any(keyword in line.lower() for keyword in ['radiolog', 'referto', 'esame', 'rx', 'tac', 'eco']):
        print(f"Line {i+1}: '{line.strip()}'")

# Test specific name patterns
print("\n🧪 TESTING NAME EXTRACTION PATTERNS:")
print("=" * 60)

name_patterns = [
    r"Nome:\s*([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)+)",
    r"(?:Nome|Paziente)[\s:.-]+([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)+)",
    r"Sig\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*)",
    r"([A-ZÀ-ÿ]{2,}\s+[A-ZÀ-ÿ]{2,}(?:\s+[A-ZÀ-ÿ]{2,})?)"
]

for i, pattern in enumerate(name_patterns):
    matches = re.findall(pattern, text, re.I | re.MULTILINE)
    print(f"Pattern {i+1}: {pattern}")
    print(f"Matches: {matches[:5]}")  # First 5 matches
    print("---")

# Test exam title patterns
print("\n🧪 TESTING EXAM TITLE PATTERNS:")
print("=" * 60)

exam_patterns = [
    r"REFERTO\s+DI\s+RADIOLOGIA",
    r"(?:REFERTO|Referto)(?:\s*di)?[\s:.-]*([A-Za-zÀ-ÿ\s]+)",
    r"(?:Tipo(?:\s*di)?(?:\s*esame|referto|indagine)?)[\s:.-]*([A-Za-zÀ-ÿ\s]+)"
]

for i, pattern in enumerate(exam_patterns):
    matches = re.findall(pattern, text, re.I | re.MULTILINE)
    print(f"Pattern {i+1}: {pattern}")
    print(f"Matches: {matches[:3]}")
    print("---")

# Now test the actual extraction function
print("\n🧪 TESTING ACTUAL EXTRACTION FUNCTION:")
print("=" * 60)

metadata = extract_metadata(file_bytes)
print(f"Patient name: {metadata.get('patient_name')}")
print(f"Report type: {metadata.get('report_type')}")
print(f"Codice fiscale: {metadata.get('codice_fiscale')}")
print(f"Report date: {metadata.get('report_date')}")
print(f"Lab values count: {len(metadata.get('laboratory_values', {}))}")
print(f"Lab values: {list(metadata.get('laboratory_values', {}).keys())[:10]}")
