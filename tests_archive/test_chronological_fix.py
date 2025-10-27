#!/usr/bin/env python3
"""
Test chronological comparison fix:
Upload newer report first, then older report, 
and verify that comparison is done chronologically (15→45, not 45→15)
"""

import requests
import json
import time

UPLOAD_URL = "http://localhost:8006/api/analyze/"

def test_chronological_comparison():
    """Test chronological comparison regardless of upload order"""
    
    print("🕐 Testing Chronological Comparison Fix")
    print("=" * 60)
    
    # Step 1: Upload NEWER report first (May 2024 - should have higher protein values)
    print("\n1️⃣ Uploading NEWER report first (May 2024):")
    try:
        with open('report_2024_05_01_modified.pdf', 'rb') as f:
            files = {'files': ('report_2024_05_01_modified.pdf', f, 'application/pdf')}
            response1 = requests.post(UPLOAD_URL, files=files)
            
        if response1.status_code == 200:
            result1 = response1.json()
            report1 = result1['risultati'][0]
            print(f"   ✅ Status: Saved={report1.get('salvato')}")
            print(f"   📅 Report Date: {report1.get('data_referto')}")
            print(f"   📋 Type: {report1.get('tipo_referto')}")
            print(f"   👤 CF: {report1.get('codice_fiscale')}")
            
            if report1.get('spiegazione'):
                print(f"   📊 Comparison: {report1.get('spiegazione')[:100]}...")
            else:
                print(f"   📊 Comparison: None (first report)")
                
        else:
            print(f"   ❌ Error: {response1.status_code}")
            print(response1.text)
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Small delay to ensure different timestamps
    time.sleep(2)
    
    # Step 2: Upload OLDER report second (Feb 2024 - should have lower protein values)
    print("\n2️⃣ Uploading OLDER report second (Feb 2024):")
    try:
        with open('report_2024_02_01.pdf', 'rb') as f:
            files = {'files': ('report_2024_02_01.pdf', f, 'application/pdf')}
            response2 = requests.post(UPLOAD_URL, files=files)
            
        if response2.status_code == 200:
            result2 = response2.json()
            report2 = result2['risultati'][0]
            print(f"   ✅ Status: Saved={report2.get('salvato')}")
            print(f"   📅 Report Date: {report2.get('data_referto')}")
            print(f"   📋 Type: {report2.get('tipo_referto')}")
            print(f"   👤 CF: {report2.get('codice_fiscale')}")
            
            if report2.get('spiegazione'):
                print(f"   📊 Comparison: {report2.get('spiegazione')}")
                
                # Analyze the comparison result
                comparison = report2.get('spiegazione', '').lower()
                situation = report2.get('situazione', '').lower()
                
                print(f"\n🔍 Analysis of Comparison:")
                print(f"   📈 Situation: {situation}")
                
                if 'aumentate' in comparison or 'aumentat' in comparison:
                    if 'da 15' in comparison and 'a 45' in comparison:
                        print(f"   ✅ CORRECT: Shows increase from 15→45 (chronologically correct)")
                    elif 'da 45' in comparison and 'a 15' in comparison:
                        print(f"   ❌ WRONG: Still shows decrease from 45→15 (upload order, not chronological)")
                    else:
                        print(f"   ❓ UNCLEAR: Mentions increase but values unclear")
                        
                elif 'diminuite' in comparison or 'diminuit' in comparison:
                    if 'da 45' in comparison and 'a 15' in comparison:
                        print(f"   ❌ WRONG: Shows decrease from 45→15 (upload order, not chronological)")
                    elif 'da 15' in comparison and 'a 45' in comparison:
                        print(f"   ✅ CORRECT: Shows increase from 15→45 (but says decreased - logic error)")
                    else:
                        print(f"   ❓ UNCLEAR: Mentions decrease but values unclear")
                        
                if situation == 'peggiorata':
                    print(f"   ✅ CORRECT: Situation marked as 'peggiorata' (15→45 is worsening)")
                elif situation == 'migliorata':
                    print(f"   ❌ WRONG: Situation marked as 'migliorata' (should be peggiorata for 15→45)")
                else:
                    print(f"   ❓ UNCLEAR: Situation is '{situation}'")
                    
            else:
                print(f"   ⚠️ No comparison provided")
                
        else:
            print(f"   ❌ Error: {response2.status_code}")
            print(response2.text)
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n📋 Expected Correct Behavior:")
    print(f"   📅 Chronological order: Feb 2024 (15.0) → May 2024 (45.0)")
    print(f"   📈 Expected comparison: 'aumentate da 15.0 a 45.0 mg/dl'")
    print(f"   📊 Expected situation: 'peggiorata' (higher protein = worse kidney function)")
    print(f"   🎯 Goal: Compare based on medical dates, not upload order")

if __name__ == "__main__":
    test_chronological_comparison()
