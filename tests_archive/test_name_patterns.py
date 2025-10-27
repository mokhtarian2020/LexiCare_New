#!/usr/bin/env python3
"""
Simplified test for the PDF parser patterns to debug the boundary issues
"""

import re

# Test just the name patterns
def test_name_extraction():
    """Test name pattern extraction with simpler patterns"""
    
    # Improved name patterns with better boundary detection
    name_patterns = [
        # Use non-greedy matching and better boundaries
        r"Sig\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.)",
        r"Dott\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.)",
        r"Dr\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.)",
        r"Dr\.ssa\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.)",
        r"(?:Paziente|Nome)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.)",
        r"(?:Assistito)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.)"
    ]
    
    test_texts = [
        "Sig. MARIO ROSSI\nD.Nasc.: 15/03/1980",
        "Dott. ANDREA VERDI\nNato il: 08-07-1990", 
        "Dr.ssa FRANCESCA NERI\nNata a Roma il: 22.05.1985",
        "Assistito: LUCA FERRARI\nD.N.: 10/01/1992",
        "Paziente: GIULIA BIANCHI\nData di nascita: 25/12/1975"
    ]
    
    expected_names = [
        "MARIO ROSSI",
        "ANDREA VERDI", 
        "FRANCESCA NERI",
        "LUCA FERRARI",
        "GIULIA BIANCHI"
    ]
    
    print("🔍 Testing Name Extraction Patterns")
    print("=" * 40)
    
    for i, (text, expected) in enumerate(zip(test_texts, expected_names)):
        print(f"\nTest {i+1}: {text.replace(chr(10), ' | ')}")
        print(f"Expected: {expected}")
        
        found_name = None
        for pattern in name_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                found_name = match.group(1).strip().upper()
                print(f"✅ Found: {found_name} (pattern: {pattern[:30]}...)")
                break
        
        if not found_name:
            print("❌ No name found")
        elif found_name.replace(" ", "") == expected.replace(" ", ""):
            print("✅ Match!")
        else:
            print(f"❌ Mismatch: got '{found_name}', expected '{expected}'")
        
        print("-" * 40)

if __name__ == "__main__":
    test_name_extraction()
