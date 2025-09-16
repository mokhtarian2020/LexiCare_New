#!/usr/bin/env python3
"""
Test script for the enhanced PDF parser patterns
Tests various Italian medical document formats
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.pdf_parser import extract_metadata
import re

# Test text samples that simulate various Italian medical documents
test_documents = [
    {
        "name": "Standard Hospital Report",
        "text": """
AZIENDA OSPEDALIERA UNIVERSITARIA
REFERTO DI RADIOLOGIA

Paziente: MARIO ROSSI
D.Nasc.: 15/03/1980
Codice Fiscale: RSSMRA80C15H501Z
Data esame: 12/11/2024
Refertato il: 13/11/2024

RADIOGRAFIA TORACE
Il paziente presenta...
        """,
        "expected": {
            "patient_name": "Mario Rossi",
            "birth_date": "15/03/1980",
            "codice_fiscale": "RSSMRA80C15H501Z",
            "report_date": "13/11/2024"
        }
    },
    {
        "name": "Laboratory Report with Formal Address",
        "text": """
LABORATORIO ANALISI CLINICHE
Via Roma, 123 - Milano

Sig. GIULIA BIANCHI
Data di nascita: 25/12/1975
CF: BNCGLI75T65F205X
Eseguito il: 10.11.2024
Prestazione effettuata il: 10/11/2024

EMOCROMO COMPLETO
Risultati delle analisi...
        """,
        "expected": {
            "patient_name": "Giulia Bianchi",
            "birth_date": "25/12/1975",
            "codice_fiscale": "BNCGLI75T65F205X",
            "report_date": "10/11/2024"
        }
    },
    {
        "name": "Cardiology Report with Alternative Patterns",
        "text": """
CENTRO CARDIOLOGICO
Dott. ANDREA VERDI
Nato il: 08-07-1990
Cod. Fiscale: VRDNDR90L08H501W
Visitato il: 05/11/2024

ELETTROCARDIOGRAMMA
Tracciato nella norma...
        """,
        "expected": {
            "patient_name": "Andrea Verdi",
            "birth_date": "08/07/1990",
            "codice_fiscale": "VRDNDR90L08H501W",
            "report_date": "05/11/2024"
        }
    },
    {
        "name": "Gynecology Report with Complex Format",
        "text": """
AMBULATORIO GINECOLOGICO
Dr.ssa FRANCESCA NERI
Nata a Roma il: 22.05.1985
C.F.: NREFRN85E62H501Y
In data: 15/11/2024
Controllo effettuato il: 15/11/2024

PAP TEST
Esame citologico...
        """,
        "expected": {
            "patient_name": "Francesca Neri",
            "birth_date": "22/05/1985",
            "codice_fiscale": "NREFRN85E62H501Y",
            "report_date": "15/11/2024"
        }
    },
    {
        "name": "Orthopedic Report with Multiline Format",
        "text": """
CENTRO ORTOPEDICO
Assistito: LUCA FERRARI
D.N.: 10/01/1992
Codice Fiscale:
FRRLCU92A10H501Q
Appuntamento del: 08/11/2024

RADIOGRAFIA GINOCCHIO
L'esame evidenzia...
        """,
        "expected": {
            "patient_name": "Luca Ferrari",
            "birth_date": "10/01/1992",
            "codice_fiscale": "FRRLCU92A10H501Q",
            "report_date": "08/11/2024"
        }
    }
]

def test_pattern_extraction():
    """Test the enhanced PDF parser patterns"""
    print("🧪 Testing Enhanced PDF Parser Patterns")
    print("=" * 50)
    
    for i, doc in enumerate(test_documents, 1):
        print(f"\n📄 Test {i}: {doc['name']}")
        print("-" * 30)
        
        # Create a fake PDF file content
        fake_pdf_bytes = doc['text'].encode('utf-8')
        
        try:
            # Note: This won't work as a real PDF but we can test the text patterns
            # For testing, we'll extract patterns directly from text
            text = doc['text']
            
            # Test patient name extraction using improved patterns
            name_patterns = [
                r"Sig\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
                r"Sig\.ra\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
                r"Dott\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
                r"Dr\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
                r"Dr\.ssa\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
                r"(?:Paziente|Nome)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
                r"(?:Assistito|Soggetto)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)"
            ]
            
            patient_name = None
            for pattern in name_patterns:
                name_match = re.search(pattern, text, re.I)
                if name_match:
                    raw_name = name_match.group(1).strip()
                    cleaned_name = re.sub(r'\s+', ' ', raw_name).title()
                    if (len(cleaned_name) >= 3 and len(cleaned_name) <= 50 and 
                        not re.search(r'\d', cleaned_name) and
                        not re.search(r'[^\w\sÀ-ÿ\'-]', cleaned_name)):
                        patient_name = cleaned_name
                        break
            
            # Test birth date extraction
            birth_date_patterns = [
                r"(?:D\.?\s*Nasc\.?|Data di nascita|Nato il|Nata il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:DN|d\.n\.|D\.N\.)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Nato a).*?(?:il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Nata a).*?(?:il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
            ]
            
            birth_date = None
            for pattern in birth_date_patterns:
                birth_match = re.search(pattern, text, re.I)
                if birth_match:
                    raw_birth_date = birth_match.group(1)
                    normalized_birth_date = re.sub(r'[.-]', '/', raw_birth_date)
                    birth_date = normalized_birth_date
                    break
            
            # Test codice fiscale extraction
            cf_pattern = re.compile(r"(?:C(?:ODICE)?\s*F(?:ISCALE)?|CF|C\.F\.)[\s:.-]*([A-Z]{6}\s*\d{2}\s*[A-Z]\s*\d{2}\s*[A-Z]\s*\d{3}\s*[A-Z])", re.I)
            cf_match = cf_pattern.search(text)
            codice_fiscale = None
            if cf_match:
                codice_fiscale = re.sub(r"[\s\-_\.]+", "", cf_match.group(1).upper())
            
            # Test report date extraction
            date_patterns = [
                r"(?:Data esame|Data referto|Refertato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Eseguito il|Effettuato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Visitato il|In data)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Controllo effettuato il|Appuntamento del)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
                r"(?:Prestazione effettuata il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
            ]
            
            report_date = None
            for pattern in date_patterns:
                date_match = re.search(pattern, text, re.I)
                if date_match:
                    raw_report_date = date_match.group(1)
                    normalized_report_date = re.sub(r'[.-]', '/', raw_report_date)
                    report_date = normalized_report_date
                    break
                    
            # Compare results
            results = {
                "patient_name": patient_name,
                "birth_date": birth_date,
                "codice_fiscale": codice_fiscale,
                "report_date": report_date
            }
            
            print(f"✅ Extracted Results:")
            for key, value in results.items():
                expected = doc['expected'].get(key, 'N/A')
                status = "✅" if value == expected else "❌"
                print(f"  {key}: {value} {status} (expected: {expected})")
                
        except Exception as e:
            print(f"❌ Error testing document: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Pattern testing completed!")

if __name__ == "__main__":
    test_pattern_extraction()
