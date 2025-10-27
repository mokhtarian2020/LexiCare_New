#!/usr/bin/env python3
"""
Direct API test to see exactly what the /analyze endpoint returns
"""

import requests
import json

def test_api_upload():
    """Test the actual API endpoint with the PDFs"""
    
    print("🌐 Testing API Endpoint Directly")
    print("=" * 40)
    
    # API endpoint
    url = "http://localhost:8008/api/analyze/"
    
    # PDF files to upload
    pdf_files = [
        "/home/amir/Documents/amir/LexiCare/report_2024_02_01.pdf",
        "/home/amir/Documents/amir/LexiCare/report_2024_05_01_modified.pdf"
    ]
    
    # Prepare files for upload
    files = []
    for pdf_path in pdf_files:
        with open(pdf_path, 'rb') as f:
            files.append(('files', (pdf_path.split('/')[-1], f.read(), 'application/pdf')))
    
    print(f"📤 Uploading {len(files)} files to {url}")
    
    try:
        # Make the API request
        response = requests.post(url, files=files)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ API Response received")
                print("\n📋 Full Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Analyze the response structure
                print(f"\n🔍 Response Analysis:")
                if 'risultati' in result:
                    risultati = result['risultati']
                    print(f"   📊 Number of results: {len(risultati)}")
                    
                    for i, res in enumerate(risultati, 1):
                        print(f"\n   📄 Result {i}:")
                        print(f"      Saved: {res.get('salvato', 'N/A')}")
                        print(f"      Message: {res.get('messaggio', 'N/A')}")
                        print(f"      CF: {res.get('codice_fiscale', 'N/A')}")
                        print(f"      Diagnosis: {res.get('diagnosi_ai', 'N/A')[:100]}...")
                        print(f"      Classification: {res.get('classificazione_ai', 'N/A')}")
                        
                        # Check comparison fields
                        if 'situazione' in res:
                            print(f"      Comparison Status: {res.get('situazione', 'N/A')}")
                            print(f"      Comparison Explanation: {res.get('spiegazione', 'N/A')[:100]}...")
                        else:
                            print(f"      ❌ No comparison fields found!")
                            
                        # Check if there are any error indicators
                        if not res.get('salvato', False):
                            print(f"      ⚠️ Not saved - check message for reason")
                            
                else:
                    print(f"   ❌ No 'risultati' field in response")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}...")
        else:
            print(f"❌ API Error {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        print("📝 Make sure the backend server is running on localhost:8008")

if __name__ == "__main__":
    test_api_upload()
