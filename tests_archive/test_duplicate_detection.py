#!/usr/bin/env python3
"""
Test script for duplicate detection
"""

import requests
import json

# Test URLs
UPLOAD_URL = "http://localhost:8006/api/analyze/"

def test_duplicate_detection():
    """Test duplicate detection by uploading the same file twice"""
    
    print("🧪 Testing Duplicate Detection")
    print("=" * 40)
    
    # First upload
    print("\n1️⃣ First upload (should succeed):")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response1 = requests.post(UPLOAD_URL, files=files)
            
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Status: {response1.status_code}")
            print(f"📊 Results: {len(result1.get('risultati', []))} reports processed")
            for i, r in enumerate(result1.get('risultati', [])):
                print(f"   Report {i+1}: Saved={r.get('salvato')}, Status={r.get('status', 'normal')}")
                print(f"   Message: {r.get('messaggio', 'N/A')}")
        else:
            print(f"❌ Error: {response1.status_code}")
            print(response1.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Second upload (should detect duplicate)
    print("\n2️⃣ Second upload (should detect duplicate):")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response2 = requests.post(UPLOAD_URL, files=files)
            
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Status: {response2.status_code}")
            print(f"📊 Results: {len(result2.get('risultati', []))} reports processed")
            for i, r in enumerate(result2.get('risultati', [])):
                print(f"   Report {i+1}: Saved={r.get('salvato')}, Status={r.get('status', 'normal')}")
                print(f"   Message: {r.get('messaggio', 'N/A')}")
                if r.get('original_save_date'):
                    print(f"   Original save date: {r.get('original_save_date')}")
        else:
            print(f"❌ Error: {response2.status_code}")
            print(response2.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_duplicate_detection()
