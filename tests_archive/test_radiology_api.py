#!/usr/bin/env python3
"""
Simple test of radiology PDF with the analyze API endpoint.
"""

import requests
import os

# Test the radiology PDF
pdf_path = "/home/amir/Documents/amir/LexiCare_documents/EXPORT_REF/209814_Non assegnato_REFERTO DI RADIOLOGIA.pdf"

print("🧪 TESTING RADIOLOGY PDF WITH API")
print("=" * 50)

# Check if file exists
if not os.path.exists(pdf_path):
    print(f"❌ File not found: {pdf_path}")
    exit(1)

print(f"✅ File found: {os.path.basename(pdf_path)}")
print(f"📄 File size: {os.path.getsize(pdf_path):,} bytes")

# Test with the API
try:
    with open(pdf_path, 'rb') as f:
        files = [('files', (os.path.basename(pdf_path), f, 'application/pdf'))]
        
        print("\n📡 Sending to API...")
        print(f"   Endpoint: http://localhost:8008/api/analyze/")
        print(f"   File: {os.path.basename(pdf_path)}")
        
        response = requests.post(
            'http://localhost:8008/api/analyze/',
            files=files,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful!")
            print(f"📋 Full response keys: {list(result.keys())}")
            
            # Access the risultati array
            if 'risultati' in result and len(result['risultati']) > 0:
                first_result = result['risultati'][0]
                print(f"   Result keys: {list(first_result.keys())}")
                print(f"   Patient: {first_result.get('nome_paziente', 'N/A')}")
                print(f"   Type: {first_result.get('tipo_referto', 'N/A')}")
                print(f"   Date: {first_result.get('data_referto', 'N/A')}")
                print(f"   Lab values: 0 (radiology report)")
                print(f"   Diagnosis: {first_result.get('diagnosi_ai', 'N/A')[:100]}...")
                print(f"   Classification: {first_result.get('classificazione_ai', 'N/A')}")
                print(f"   Saved: {first_result.get('salvato', False)}")
                print(f"   Message: {first_result.get('messaggio', 'N/A')}")
                
                if first_result.get('comparison'):
                    print(f"   Comparison: {first_result.get('comparison', 'N/A')[:100]}...")
                else:
                    print("   Comparison: No previous reports for comparison")
            else:
                print("   No results found in response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Error: {response.text}")
            
except requests.exceptions.Timeout:
    print("❌ Timeout Error: Request took too long")
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Is the backend server running?")
    print("💡 Try: python backend/main.py")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 Test completed!")
