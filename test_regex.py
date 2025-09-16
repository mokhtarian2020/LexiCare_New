#!/usr/bin/env python3

import re

# Test the regex pattern directly
text_sample = '''Proteine: 15 * mg/dl (0 - 10)
Emoglobina: 0,50 * mg/dl (ASSENTE)
Glucosio: ASSENTE mg/dl (ASSENTE)'''

pattern = r'^([A-Za-z\s]+):\s+([0-9]+[.,]?[0-9]*|\w+)\s*(\*?)\s*([a-zA-Z%/]+)?\s*(?:\(([^)]+)\))?'

print("Testing regex pattern:")
print(f"Pattern: {pattern}")
print()

lines = text_sample.split('\n')
for i, line in enumerate(lines):
    print(f'Line {i+1}: "{line}"')
    match = re.search(pattern, line)
    if match:
        print(f'  ✅ Match found: {match.groups()}')
        test_name = match.groups()[0].strip()
        value = match.groups()[1].strip()
        abnormal_flag = match.groups()[2] if len(match.groups()) > 2 else ""
        unit = match.groups()[3] if len(match.groups()) > 3 and match.groups()[3] else ""
        reference = match.groups()[4] if len(match.groups()) > 4 and match.groups()[4] else ""
        
        print(f'  Test: {test_name}')
        print(f'  Value: {value}')
        print(f'  Abnormal flag: "{abnormal_flag}"')
        print(f'  Unit: {unit}')
        print(f'  Reference: {reference}')
    else:
        print('  ❌ No match')
    print()
