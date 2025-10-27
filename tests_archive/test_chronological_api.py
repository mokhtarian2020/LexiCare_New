#!/usr/bin/env python3
"""
Test the fixed API logic for chronological ordering
Tests uploading multiple files and ensures correct comparison based on report dates
"""
import requests
import json
import sys
import os

def test_chronological_api():
    """Test the fixed API endpoint for chronological ordering"""
    print("🧪 Testing LexiCare Chronological API Logic")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:8006/analyze-fixed"
    
    # Test files (both should exist)
    file1 = "/home/amir/Documents/amir/LexiCare/report_2024_02_01.pdf"
    file2 = "/home/amir/Documents/amir/LexiCare/report_2024_05_01_modified.pdf"
    
    # Check files exist
    for file_path in [file1, file2]:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        print(f"✅ File found: {os.path.basename(file_path)}")
    
    # Prepare files for upload (intentionally out of chronological order)
    files = [
        ('files', ('report_may_2024.pdf', open(file2, 'rb'), 'application/pdf')),
        ('files', ('report_feb_2024.pdf', open(file1, 'rb'), 'application/pdf'))
    ]
    
    try:
        print(f"\n📤 Uploading files to {url}")
        print("🔄 Files uploaded out of chronological order (May first, then Feb)")
        print("🎯 Expected: API should sort by report date and compare correctly")
        
        response = requests.post(url, files=files)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📋 API Response Summary:")
            print("=" * 30)
            
            # Print results for each report (using "risultati" not "results")
            results = data.get('risultati', [])
            for i, result in enumerate(results, 1):
                report_date = result.get('data_referto', 'Unknown')
                diagnosis = result.get('diagnosi_ai', 'No diagnosis')
                comparison = result.get('situazione', 'No comparison')
                explanation = result.get('spiegazione', 'No explanation')
                
                print(f"\n📄 Report {i}:")
                print(f"  📅 Date: {report_date}")
                print(f"  🩺 Diagnosis: {diagnosis}")
                print(f"  📊 Comparison: {comparison}")
                print(f"  💬 Explanation: {explanation[:100]}...")
                
                # Validate chronological order
                if i == 1:
                    expected_date = "01/02/2024"
                    expected_comparison = "migliorata"  # Based on debug output
                elif i == 2:
                    expected_date = "01/05/2024"
                    expected_comparison = "invariata"  # Based on debug output
                
                if report_date == expected_date:
                    print(f"  ✅ Date correct: {report_date}")
                else:
                    print(f"  ❌ Date incorrect: expected {expected_date}, got {report_date}")
                
                if expected_comparison in comparison.lower():
                    print(f"  ✅ Comparison correct: {comparison}")
                else:
                    print(f"  ❌ Comparison incorrect: expected '{expected_comparison}', got '{comparison}'")
            
            print(f"\n📊 Total reports processed: {len(results)}")
            print("🎯 Chronological Test Result:")
            
            # Check if results are in correct chronological order
            if len(results) == 2:
                date1 = results[0].get('data_referto')
                date2 = results[1].get('data_referto')
                comp1 = results[0].get('situazione', '')
                comp2 = results[1].get('situazione', '')
                
                if (date1 == "01/02/2024" and date2 == "01/05/2024" and 
                    comp1.lower() == "migliorata" and comp2.lower() == "invariata"):
                    print("✅ CHRONOLOGICAL TEST PASSED!")
                    print("   - Feb 2024 report processed first (baseline)")
                    print("   - May 2024 report processed second (compared to Feb)")
                    print("   - Comparison correctly shows sequence: improved -> stable")
                    return True
                else:
                    print("❌ CHRONOLOGICAL TEST FAILED!")
                    print(f"   - Date order: {date1} -> {date2}")
                    print(f"   - Comparisons: '{comp1}' -> '{comp2}'")
                    return False
            else:
                print(f"❌ Expected 2 results, got {len(results)}")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False
    finally:
        # Close file handles
        for file_tuple in files:
            if len(file_tuple) > 1 and hasattr(file_tuple[1][1], 'close'):
                file_tuple[1][1].close()

if __name__ == "__main__":
    success = test_chronological_api()
    if success:
        print("\n🎉 All tests passed! Chronological API logic is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Check the API logic and database state.")
        sys.exit(1)
