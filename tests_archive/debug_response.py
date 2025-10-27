#!/usr/bin/env python3
"""
Debug the API response structure.
"""

import requests
import os
import json

pdf_path = "/home/amir/Documents/amir/LexiCare_documents/EXPORT_REF/209814_Non assegnato_REFERTO DI RADIOLOGIA.pdf"

print("🔍 DEBUGGING API RESPONSE STRUCTURE", flush=True)
print("=" * 50, flush=True)

try:
    with open(pdf_path, 'rb') as f:
        files = [('files', (os.path.basename(pdf_path), f, 'application/pdf'))]
        
        response = requests.post(
            'http://localhost:8008/api/analyze/',
            files=files,
            timeout=60
        )
        
        print(f"Status: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Raw response type: {type(result)}", flush=True)
            print(f"Raw response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}", flush=True)
            print(f"Raw response (first 500 chars): {str(result)[:500]}...", flush=True)
            
            # Pretty print the full response
            print("\nFull JSON Response:", flush=True)
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        else:
            print(f"Error: {response.text}", flush=True)
            
except Exception as e:
    print(f"Exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
