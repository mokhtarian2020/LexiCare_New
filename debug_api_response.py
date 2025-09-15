#!/usr/bin/env python3
"""
Debug the API response to see what's happening
"""
import requests
import json
import os

def debug_api_response():
    """Debug the API response to see the actual data"""
    print("🔍 Debugging LexiCare API Response")
    print("=" * 40)
    
    # API endpoint
    url = "http://localhost:8006/analyze-fixed"
    
    # Test files
    file1 = "/home/amir/Documents/amir/LexiCare/report_2024_02_01.pdf"
    file2 = "/home/amir/Documents/amir/LexiCare/report_2024_05_01_modified.pdf"
    
    # Prepare files for upload
    files = [
        ('files', ('report_may_2024.pdf', open(file2, 'rb'), 'application/pdf')),
        ('files', ('report_feb_2024.pdf', open(file1, 'rb'), 'application/pdf'))
    ]
    
    try:
        print(f"📤 Sending request to {url}")
        response = requests.post(url, files=files)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n📄 Raw Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📄 Raw text response: {response.text}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")
    finally:
        # Close file handles
        for file_tuple in files:
            if len(file_tuple) > 1 and hasattr(file_tuple[1][1], 'close'):
                file_tuple[1][1].close()

if __name__ == "__main__":
    debug_api_response()
