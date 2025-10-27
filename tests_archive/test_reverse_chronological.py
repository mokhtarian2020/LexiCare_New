#!/usr/bin/env python3
"""
Test reverse chronological order:
Upload older report first, then newer report,
and verify that comparison is still chronologically correct (15→45)
"""

import requests
import json
import time

UPLOAD_URL = "http://localhost:8006/api/analyze/"

def test_reverse_chronological():
    """Test chronological comparison with reverse upload order"""
    
    print("🔄 Testing Reverse Upload Order")
    print("=" * 50)
    
    # Step 1: Upload OLDER report first (Feb 2024)
    print("\n1️⃣ Uploading OLDER report first (Feb 2024):")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response1 = requests.post(UPLOAD_URL, files=files)
            
        if response1.status_code == 200:
            result1 = response1.json()
            report1 = result1['risultati'][0]
            print(f"   ✅ Status: Saved={report1.get('salvato')}")
            print(f"   📅 Report Date: {report1.get('data_referto')}")
            print(f"   📊 Comparison: {report1.get('spiegazione', 'None (first report)')}")
        else:
            print(f"   ❌ Error: {response1.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    time.sleep(2)
    
    # Step 2: Upload NEWER report second (May 2024)
    print("\n2️⃣ Uploading NEWER report second (May 2024):")
    try:
        with open('report_2024_05_01_modified.pdf', 'rb') as f:
            files = {'files': ('report_2024_05_01_modified.pdf', f, 'application/pdf')}
            response2 = requests.post(UPLOAD_URL, files=files)
            
        if response2.status_code == 200:
            result2 = response2.json()
            report2 = result2['risultati'][0]
            print(f"   ✅ Status: Saved={report2.get('salvato')}")
            print(f"   📅 Report Date: {report2.get('data_referto')}")
            print(f"   📊 Comparison: {report2.get('spiegazione', 'No comparison')}")
            print(f"   📈 Situation: {report2.get('situazione', 'No situation')}")
            
            # This should still show 15→45 increase (peggiorata)
            comparison = report2.get('spiegazione', '').lower()
            situation = report2.get('situazione', '').lower()
            
            print(f"\n🔍 Verification:")
            if 'da 15' in comparison and 'a 45' in comparison:
                print(f"   ✅ CORRECT: Shows chronological progression 15→45")
            elif 'da 45' in comparison and 'a 15' in comparison:
                print(f"   ❌ WRONG: Shows reverse progression 45→15")
            else:
                print(f"   ❓ Values not clear in comparison text")
                
            if situation == 'peggiorata':
                print(f"   ✅ CORRECT: Marked as worsening")
            else:
                print(f"   ❓ Situation: {situation}")
            
        else:
            print(f"   ❌ Error: {response2.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_reverse_chronological()
