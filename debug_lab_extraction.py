#!/usr/bin/env python3
"""
Debug the laboratory value extraction specifically
"""

import sys
import re
sys.path.append('backend')

# Test the extraction function directly
def debug_lab_extraction():
    """Debug lab value extraction with the real PDF text"""
    
    # Real urine analysis text from PDF 1
    urine_text = """ESAME CHIMICO FISICO DELLE URINE
Colore
  GIALLO PAGLIERINO
Aspetto
  VELATO 
Ph
  5,5 
5.5 - 6.5
Glucosio
  ASSENTE 
mg/dl
ASSENTE
Proteine
  30 *
mg/dl
0 - 10
Emoglobina
  0,50 *
mg/dl
ASSENTE
Corpi Chetonici
  ASSENTI 
mg/dl
ASSENTE
Bilirubina
  ASSENTE 
mg/dl
ASSENTE
Urobilinogeno
  0,20 
EU/dl
0 - 1.0
Peso Specifico
  1,019 
1.005 - 1.020
Nitriti
  ASSENTI 
Assenti
Esterasi Leucocitaria
  75,0 *
Leu/ul"""
    
    print("🔬 Debug Laboratory Value Extraction")
    print("=" * 50)
    print("Sample text:")
    print(urine_text)
    print("\n" + "=" * 50)
    
    # Test different patterns manually
    patterns = [
        # Pattern 1: Test name on one line, value on next
        (r'(Colore|Aspetto|Ph|Glucosio|Proteine|Emoglobina|Corpi Chetonici|Bilirubina|Urobilinogeno|Peso Specifico|Nitriti|Esterasi Leucocitaria)\s*\n\s*([^\n]+)', 'multiline'),
        
        # Pattern 2: Test name and value on same line
        (r'(Ph)\s+([0-9]+[.,][0-9]+)', 'same_line'),
        
        # Pattern 3: Any word followed by number
        (r'([A-Za-z]+)\s+([0-9]+[.,]?[0-9]*)', 'word_number'),
        
        # Pattern 4: Test specific urinalysis
        (r'([A-Za-z\s]+?)\s*\n\s*([A-Z\s]+|[0-9]+[.,]?[0-9]*\s*\*?)', 'urine_specific')
    ]
    
    for pattern_name, pattern_regex in patterns:
        print(f"\n🧪 Testing pattern: {pattern_name}")
        print(f"Regex: {pattern_regex}")
        
        matches = re.findall(pattern_regex, urine_text, re.MULTILINE | re.IGNORECASE)
        print(f"Found {len(matches)} matches:")
        
        for i, match in enumerate(matches[:10]):  # Show first 10
            print(f"  {i+1}: {match}")
        
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more")
    
    print("\n" + "=" * 50)
    print("🎯 Manual extraction attempt:")
    
    # Manual extraction for urinalysis
    lines = urine_text.split('\n')
    extracted_values = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this line is a test name
        test_names = ['Colore', 'Aspetto', 'Ph', 'Glucosio', 'Proteine', 'Emoglobina', 
                     'Corpi Chetonici', 'Bilirubina', 'Urobilinogeno', 'Peso Specifico', 
                     'Nitriti', 'Esterasi Leucocitaria']
        
        for test_name in test_names:
            if line.startswith(test_name):
                # Look for value on next line or same line
                value = None
                unit = None
                reference = None
                
                # Check if value is on same line
                remaining = line[len(test_name):].strip()
                if remaining:
                    value = remaining
                # Check next line
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(next_line.startswith(tn) for tn in test_names):
                        value = next_line
                        
                        # Check for unit/reference on subsequent lines
                        if i + 2 < len(lines):
                            unit_line = lines[i + 2].strip()
                            if unit_line and len(unit_line) < 20:  # Likely a unit
                                unit = unit_line
                                
                        if i + 3 < len(lines):
                            ref_line = lines[i + 3].strip()
                            if ref_line and ('-' in ref_line or ref_line in ['ASSENTE', 'Assenti']):
                                reference = ref_line
                
                if value:
                    abnormal = '*' in value
                    extracted_values[test_name] = {
                        'value': value.replace('*', '').strip(),
                        'unit': unit or '',
                        'reference': reference or '',
                        'abnormal': abnormal
                    }
                    print(f"  ✅ {test_name}: {value} {unit or ''} {reference or ''}")
                break
        i += 1
    
    print(f"\n📊 Manual extraction found {len(extracted_values)} values")
    return extracted_values

if __name__ == "__main__":
    debug_lab_extraction()
