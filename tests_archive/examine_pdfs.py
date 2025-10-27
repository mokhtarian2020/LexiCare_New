#!/usr/bin/env python3

import fitz

# PDF 2
try:
    doc = fitz.open('1907122220448610ODM_5d298ea87d27f1ac3151d6f4.pdf')
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    print('PDF 2 - Text length:', len(text))
    print('Full text:')
    print(text)
except Exception as e:
    print(f"Error: {e}")
