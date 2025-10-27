#!/usr/bin/env python3
"""
Simple test to verify the backend is working correctly.
"""

import requests
import os
import sys

# Test the radiology PDF
pdf_path = "/home/amir/Documents/amir/LexiCare_documents/EXPORT_REF/209814_Non assegnato_REFERTO DI RADIOLOGIA.pdf"

print("🧪 TESTING BACKEND FUNCTIONALITY", flush=True)
print("=" * 50, flush=True)

# First test simple GET
print("1️⃣ Testing root endpoint...", flush=True)
try:
    response = requests.get('http://localhost:8008/', timeout=5)
    print(f"   Status: {response.status_code}", flush=True)
    print(f"   Response: {response.json()}", flush=True)
except Exception as e:
    print(f"   ❌ Error: {e}", flush=True)
    sys.exit(1)

# Test file upload
if os.path.exists(pdf_path):
    print("\n2️⃣ Testing file upload...", flush=True)
    try:
        with open(pdf_path, 'rb') as f:
            files = [('files', (os.path.basename(pdf_path), f, 'application/pdf'))]
            print(f"   Uploading: {os.path.basename(pdf_path)}", flush=True)
            
            response = requests.post(
                'http://localhost:8008/api/analyze/',
                files=files,
                timeout=60
            )
            
            print(f"   Status: {response.status_code}", flush=True)
            
            if response.status_code == 200:
                result = response.json()
                if 'risultati' in result and len(result['risultati']) > 0:
                    first_result = result['risultati'][0]
                    print(f"   ✅ Patient: {first_result.get('patient_name', 'N/A')}", flush=True)
                    print(f"   ✅ Type: {first_result.get('report_type', 'N/A')}", flush=True)
                    print(f"   ✅ Date: {first_result.get('report_date', 'N/A')}", flush=True)
                    print(f"   ✅ Diagnosis: {first_result.get('ai_diagnosis', 'N/A')[:80]}...", flush=True)
                else:
                    print(f"   ❌ No results in response", flush=True)
            else:
                print(f"   ❌ Error: {response.text}", flush=True)
                
    except Exception as e:
        print(f"   ❌ Exception: {e}", flush=True)
else:
    print(f"\n❌ File not found: {pdf_path}", flush=True)

print("\n🎉 Test completed!", flush=True)
