#!/usr/bin/env python3
"""
Debug the AI comparison by showing exactly what text is being compared
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.pdf_parser import extract_metadata
from backend.core.comparator import _perform_comparison
import json

def debug_ai_comparison():
    """Debug what text the AI is actually comparing"""
    
    print("🔍 Debugging AI Comparison - What Text is Being Compared")
    print("=" * 65)
    
    # Your PDF files
    pdf_files = [
        "/home/amir/Documents/amir/LexiCare/report_2024_02_01.pdf",  # proteine 15
        "/home/amir/Documents/amir/LexiCare/report_2024_05_01.pdf"   # proteine 45
    ]
    
    extracted_texts = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 EXTRACTING TEXT FROM PDF {i}:")
        print("-" * 40)
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        meta = extract_metadata(pdf_bytes)
        full_text = meta.get('full_text', '')
        
        print(f"📝 Extracted text ({len(full_text)} chars):")
        print("─" * 30)
        print(full_text)
        print("─" * 30)
        
        extracted_texts.append(full_text)
    
    if len(extracted_texts) == 2:
        print(f"\n🤖 TESTING AI COMPARISON:")
        print("-" * 30)
        
        previous_text = extracted_texts[0]
        current_text = extracted_texts[1]
        
        print("🔸 Previous report text:")
        print(f"   {previous_text[:100]}...")
        print("🔸 Current report text:")
        print(f"   {current_text[:100]}...")
        
        print(f"\n🔄 Calling AI comparison...")
        try:
            # Test with a simpler comparison first
            result = _perform_comparison(previous_text, current_text)
            print(f"✅ AI Response:")
            print(f"   Status: {result.get('status', 'Unknown')}")
            print(f"   Explanation: {result.get('explanation', 'No explanation')}")
            
        except Exception as e:
            print(f"❌ AI Error: {str(e)}")
            
            # Try direct Ollama call to see what's happening
            print(f"\n🔧 Testing direct Ollama call...")
            try:
                import ollama
                simple_prompt = "Confronta due referti medici e rispondi in JSON: {'status': 'migliorata', 'explanation': 'test'}"
                
                response = ollama.generate(model="alibayram/medgemma", prompt=simple_prompt)
                raw_response = response.get("response", "")
                
                print(f"📝 Raw Ollama response: '{raw_response}'")
                print(f"📊 Response length: {len(raw_response)}")
                
                if not raw_response.strip():
                    print("⚠️ AI returned empty response!")
                else:
                    try:
                        parsed = json.loads(raw_response.strip())
                        print(f"✅ Valid JSON: {parsed}")
                    except json.JSONDecodeError as je:
                        print(f"❌ Invalid JSON: {je}")
                        print(f"   First 200 chars: '{raw_response[:200]}'")
                        
            except Exception as e2:
                print(f"❌ Direct Ollama error: {str(e2)}")

if __name__ == "__main__":
    debug_ai_comparison()
