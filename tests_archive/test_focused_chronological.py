#!/usr/bin/env python3
"""
Focused Chronological Test
===========================
Tests chronological comparison in isolation to verify the fix works correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8006"

def test_chronological_upload(file1, file2, test_description):
    """Test chronological upload order"""
    print(f"\n🔍 {test_description}")
    print("=" * 60)
    
    # First upload
    print(f"\n1️⃣ Uploading first report:")
    try:
        with open(file1, 'rb') as file:
            files = {'files': (file1.split('/')[-1], file, 'application/pdf')}
            response1 = requests.post(f"{BASE_URL}/api/analyze", files=files, timeout=30)
        
        if response1.status_code == 200:
            result1 = response1.json()
            if result1.get('risultati'):
                r1 = result1['risultati'][0]
                print(f"   ✅ Saved: {r1.get('salvato', False)}")
                print(f"   📋 Type: {r1.get('tipo_referto', 'N/A')}")
                print(f"   💬 Message: {r1.get('messaggio', 'N/A')[:80]}...")
        else:
            print(f"   ❌ Error: {response1.status_code}")
            return
    
    except Exception as e:
        print(f"   ⚠️ Exception: {e}")
        return
    
    time.sleep(2)  # Wait between uploads
    
    # Second upload
    print(f"\n2️⃣ Uploading second report:")
    try:
        with open(file2, 'rb') as file:
            files = {'files': (file2.split('/')[-1], file, 'application/pdf')}
            response2 = requests.post(f"{BASE_URL}/api/analyze", files=files, timeout=30)
        
        if response2.status_code == 200:
            result2 = response2.json()
            if result2.get('risultati'):
                r2 = result2['risultati'][0]
                print(f"   ✅ Saved: {r2.get('salvato', False)}")
                print(f"   📊 Status: {r2.get('status', 'unknown')}")
                print(f"   📋 Type: {r2.get('tipo_referto', 'N/A')}")
                print(f"   💬 Message: {r2.get('messaggio', 'N/A')[:80]}...")
                
                # Check for comparison results (situazione/spiegazione)
                if r2.get('situazione') and r2.get('spiegazione'):
                    print(f"\n   📊 COMPARISON FOUND:")
                    print(f"      📈 Status: {r2.get('situazione', 'N/A')}")
                    print(f"      📝 Explanation: {r2.get('spiegazione', 'N/A')}")
                    
                    # Analyze the comparison
                    explanation = r2.get('spiegazione', '')
                    if '15.0 a 45.0' in explanation and 'aumentate' in explanation:
                        print(f"      ✅ CHRONOLOGICAL ORDER: Correct (15→45)")
                    elif '45.0 a 15.0' in explanation:
                        print(f"      ❌ CHRONOLOGICAL ORDER: Wrong (45→15)")
                    else:
                        print(f"      ❓ CHRONOLOGICAL ORDER: Cannot determine from text")
                        print(f"      🔍 Debug - explanation content: {explanation[:200]}...")
                else:
                    print(f"   ❌ No comparison found (situazione: {r2.get('situazione', 'N/A')})")
        else:
            print(f"   ❌ Error: {response2.status_code}")
            return
    
    except Exception as e:
        print(f"   ⚠️ Exception: {e}")
        return

def main():
    print("🧪 FOCUSED CHRONOLOGICAL COMPARISON TEST")
    print("=" * 60)
    
    # Test 1: Upload newer report first, then older report
    test_chronological_upload(
        "report_2024_05_01.pdf", 
        "report_2024_02_01.pdf",
        "TEST 1: Upload May 2024 (newer) → Feb 2024 (older)"
    )
    
    print("\n" + "="*60)
    print("⏱️ Waiting 5 seconds before next test...")
    time.sleep(5)
    
    # Clean database for second test
    print("\n🧹 Cleaning database for second test...")
    import subprocess
    subprocess.run(["python", "cleanup_complete.py"], capture_output=True)
    time.sleep(2)
    
    # Test 2: Upload older report first, then newer report
    test_chronological_upload(
        "report_2024_02_01.pdf",
        "report_2024_05_01.pdf", 
        "TEST 2: Upload Feb 2024 (older) → May 2024 (newer)"
    )
    
    print(f"\n📋 CONCLUSION:")
    print(f"Both tests should show chronological order 15→45 regardless of upload sequence")

if __name__ == "__main__":
    main()
