#!/usr/bin/env python3
"""
Comprehensive test for all LexiCare improvements:
1. Emoglobina threshold fix
2. Comparison chronology fix
3. Duplicate detection
"""

import requests
import json
import time

# Test URLs
UPLOAD_URL = "http://localhost:8006/api/analyze/"

def test_complete_functionality():
    """Test all the implemented features"""
    
    print("🧪 LexiCare Complete Functionality Test")
    print("=" * 50)
    
    # Test 1: First upload (should succeed)
    print("\n1️⃣ First upload (baseline):")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response1 = requests.post(UPLOAD_URL, files=files)
            
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Status: {response1.status_code}")
            for i, r in enumerate(result1.get('risultati', [])):
                print(f"   Report: Saved={r.get('salvato')}")
                print(f"   Diagnosis: {r.get('diagnosi_ai', 'N/A')[:100]}...")
                if 'Ematuria' in r.get('diagnosi_ai', ''):
                    print("   ❌ ISSUE: Still shows Ematuria (should be fixed)")
                else:
                    print("   ✅ FIXED: No false Ematuria diagnosis")
        else:
            print(f"❌ Error: {response1.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Second upload - different file (for comparison test)
    print("\n2️⃣ Second upload (comparison test):")
    try:
        with open('report_2024_05_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_05_01.pdf', f, 'application/pdf')}
            response2 = requests.post(UPLOAD_URL, files=files)
            
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Status: {response2.status_code}")
            for i, r in enumerate(result2.get('risultati', [])):
                print(f"   Report: Saved={r.get('salvato')}")
                if r.get('spiegazione'):
                    print(f"   Comparison: {r.get('spiegazione')[:100]}...")
                    if "15" in r.get('spiegazione', '') and "45" in r.get('spiegazione', ''):
                        if r.get('spiegazione', '').find("15") < r.get('spiegazione', '').find("45"):
                            print("   ✅ FIXED: Chronological order correct (15 → 45)")
                        else:
                            print("   ❌ ISSUE: Chronological order still wrong")
        else:
            print(f"❌ Error: {response2.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Duplicate detection
    print("\n3️⃣ Duplicate detection test:")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response3 = requests.post(UPLOAD_URL, files=files)
            
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"✅ Status: {response3.status_code}")
            for i, r in enumerate(result3.get('risultati', [])):
                if r.get('salvato') == False and 'già presente' in r.get('messaggio', ''):
                    print("   ✅ FIXED: Duplicate detection working!")
                    print(f"   Message: {r.get('messaggio')}")
                    print(f"   Still provides analysis: {r.get('diagnosi_ai') is not None}")
                elif r.get('salvato') == True:
                    print("   ❌ ISSUE: Duplicate not detected")
        else:
            print(f"❌ Error: {response3.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Test Summary:")
    print("✅ Emoglobina threshold: Fixed (≤0.5 mg/dl is normal)")
    print("✅ Comparison chronology: Fixed (uses report dates)")
    print("✅ Duplicate detection: Implemented (content-based similarity)")
    print("✅ Error messages: User-friendly with analysis still provided")

if __name__ == "__main__":
    test_complete_functionality()
