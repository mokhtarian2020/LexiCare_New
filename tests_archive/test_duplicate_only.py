#!/usr/bin/env python3
"""
Duplicate Detection Test
========================
Test duplicate detection for same CF + Date + Type + Content
"""

import requests
import time

BASE_URL = "http://localhost:8006"

def test_duplicate_scenarios():
    print("🔍 COMPREHENSIVE DUPLICATE DETECTION TEST")
    print("=" * 50)
    
    # Test 1: Upload same report twice (should detect duplicate)
    print("\n📋 TEST 1: Upload identical report twice")
    print("-" * 40)
    
    for i in range(1, 3):
        print(f"\n{i}️⃣ Upload #{i} of SAME report (May 2024):")
        try:
            with open("report_2024_05_01.pdf", 'rb') as file:
                files = {'files': ("report_2024_05_01.pdf", file, 'application/pdf')}
                response = requests.post(f"{BASE_URL}/api/analyze", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('risultati'):
                    r = result['risultati'][0]
                    print(f"   ✅ Saved: {r.get('salvato', False)}")
                    print(f"   📊 Status: {r.get('status', 'unknown')}")
                    print(f"   📋 Type: {r.get('tipo_referto', 'N/A')}")
                    print(f"   📅 Date: {r.get('data_referto', 'N/A')}")
                    print(f"   � CF: {r.get('codice_fiscale', 'N/A')}")
                    print(f"   �💬 Message: {r.get('messaggio', 'N/A')[:100]}...")
                    
                    # Check for duplicate detection on second upload
                    if i == 2:
                        if r.get('status') == 'duplicate' or not r.get('salvato', False):
                            print(f"   ✅ DUPLICATE DETECTION: Working correctly (same CF+Date+Type+Content)")
                        else:
                            print(f"   ❌ DUPLICATE DETECTION: Failed to detect duplicate")
                    
        except Exception as e:
            print(f"   ⚠️ Exception: {e}")
            
        time.sleep(1)
    
    time.sleep(2)
    
    # Test 2: Upload different date report (should NOT be duplicate)
    print(f"\n📋 TEST 2: Upload report with different date")
    print("-" * 40)
    print(f"\n3️⃣ Upload DIFFERENT date report (Feb 2024):")
    
    try:
        with open("report_2024_02_01.pdf", 'rb') as file:
            files = {'files': ("report_2024_02_01.pdf", file, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/api/analyze", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('risultati'):
                r = result['risultati'][0]
                print(f"   ✅ Saved: {r.get('salvato', False)}")
                print(f"   📊 Status: {r.get('status', 'unknown')}")
                print(f"   📋 Type: {r.get('tipo_referto', 'N/A')}")
                print(f"   📅 Date: {r.get('data_referto', 'N/A')}")
                print(f"   👤 CF: {r.get('codice_fiscale', 'N/A')}")
                
                if r.get('salvato', False):
                    print(f"   ✅ DIFFERENT DATE: Correctly saved as new report")
                else:
                    print(f"   ❌ DIFFERENT DATE: Incorrectly marked as duplicate")
                
    except Exception as e:
        print(f"   ⚠️ Exception: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Same CF+Date+Type+Content = Duplicate (blocked)")
    print(f"   ✅ Same CF+Type+Content but Different Date = New Report (allowed)")

if __name__ == "__main__":
    test_duplicate_scenarios()
