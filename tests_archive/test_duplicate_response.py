#!/usr/bin/env python3
"""
Test duplicate detection response to see what's being sent to frontend
"""

import requests
import json

UPLOAD_URL = "http://localhost:8006/api/analyze/"

def test_duplicate_response():
    """Test what response is sent for duplicate detection"""
    
    print("🧪 Testing Duplicate Detection Response")
    print("=" * 50)
    
    # First upload
    print("\n1️⃣ First upload:")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response1 = requests.post(UPLOAD_URL, files=files)
            
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Status: {response1.status_code}")
            print(f"📄 Response keys: {list(result1.keys())}")
            print(f"📊 Results count: {len(result1.get('risultati', []))}")
            
            for i, report in enumerate(result1.get('risultati', [])):
                print(f"\n📋 Report {i+1}:")
                print(f"   salvato: {report.get('salvato')}")
                print(f"   messaggio: {report.get('messaggio')}")
                print(f"   codice_fiscale: {report.get('codice_fiscale')}")
                print(f"   status: {report.get('status', 'None')}")
                
        else:
            print(f"❌ Error: {response1.status_code}")
            print(response1.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Second upload (should be duplicate)
    print("\n2️⃣ Second upload (duplicate):")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response2 = requests.post(UPLOAD_URL, files=files)
            
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Status: {response2.status_code}")
            print(f"📄 Response keys: {list(result2.keys())}")
            print(f"📊 Results count: {len(result2.get('risultati', []))}")
            
            for i, report in enumerate(result2.get('risultati', [])):
                print(f"\n📋 Report {i+1}:")
                print(f"   salvato: {report.get('salvato')}")
                print(f"   messaggio: {report.get('messaggio')}")
                print(f"   codice_fiscale: {report.get('codice_fiscale')}")
                print(f"   status: {report.get('status', 'None')}")
                print(f"   original_save_date: {report.get('original_save_date', 'None')}")
                
                # Check what the frontend should see
                print(f"\n🔍 Frontend Logic Check:")
                if report.get('status') == 'duplicate':
                    print(f"   ✅ Frontend should show: DUPLICATE MESSAGE")
                elif not report.get('codice_fiscale'):
                    print(f"   ⚠️ Frontend should show: NO CF MESSAGE")
                elif not report.get('salvato'):
                    print(f"   ❓ Frontend logic unclear for this case")
                else:
                    print(f"   ✅ Frontend should show: SUCCESS MESSAGE")
                
        else:
            print(f"❌ Error: {response2.status_code}")
            print(response2.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_duplicate_response()
