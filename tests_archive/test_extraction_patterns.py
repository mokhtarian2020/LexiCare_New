#!/usr/bin/env python3
"""
Test the enhanced key value extraction for different report types
"""

import sys
import os
sys.path.append('backend')

def test_extraction_patterns():
    """Test key value extraction for different report types"""
    
    # Import our extraction function
    from api.analyze import extract_key_values_from_text
    
    print("🔬 Testing Enhanced Key Value Extraction")
    print("=" * 60)
    
    # Test cases for different report types
    test_cases = [
        {
            'name': 'Laboratory Report (Urine)',
            'type': 'Esame Chimico Fisico Delle Urine',
            'text': '''
            A.S.L. NAPOLI 1 CENTRO
            ESAME CHIMICO FISICO DELLE URINE
            Colore: GIALLO PAGLIERINO
            Aspetto: VELATO
            pH: 5,5 (5.5 - 6.5)
            Glucosio: ASSENTE mg/dl (ASSENTE)
            Proteine: 15.0 mg/dl (< 20)
            Emoglobina: 0,50 mg/dl (ASSENTE)
            Creatinina: 120 mg/dl
            ''',
            'expected_category': 'Laboratory'
        },
        {
            'name': 'Radiology Report (Ultrasound)',
            'type': 'Ecografia Addominale',
            'text': '''
            ECOGRAFIA ADDOMINALE
            Fegato: di dimensioni normali, ecostruttura omogenea
            Reni: nella norma, senza dilatazione
            Milza: normale
            Versamento peritoneale: assente
            Dimensioni vescica: 4.5 x 3.2 cm
            ''',
            'expected_category': 'Radiology'
        },
        {
            'name': 'Pathology Report (Biopsy)',
            'type': 'Biopsia Epatica Istologica',
            'text': '''
            ESAME ISTOLOGICO
            Carcinoma epatocellulare ben differenziato
            Grado: II
            Dimensioni: 2.5 cm
            Margini di resezione: liberi
            Ki-67: 15%
            Necrosi: presente focalmente
            Invasione vascolare: assente
            ''',
            'expected_category': 'Pathology'
        },
        {
            'name': 'Generic Medical Report',
            'type': 'Visita Medica Generale',
            'text': '''
            VISITA MEDICA
            Data: 15/10/2024
            Paziente: Mario Rossi
            Diagnosi: Ipertensione arteriosa
            Terapia: ACE inibitori 10 mg
            Pressione: 140/90 mmHg
            ''',
            'expected_category': 'Generic'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {case['name']}")
        print(f"   Report Type: {case['type']}")
        print(f"   Expected Category: {case['expected_category']}")
        
        # Extract key values
        try:
            key_values = extract_key_values_from_text(case['text'], case['type'])
            
            if key_values:
                print(f"   ✅ Extracted {len(key_values)} key values:")
                for key, value in key_values.items():
                    print(f"      • {key}: {value}")
            else:
                print(f"   ⚠️ No key values extracted")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   🧪 Laboratory: Extracts numerical test results")
    print(f"   🔍 Radiology: Extracts anatomical findings and measurements") 
    print(f"   🔬 Pathology: Extracts diagnostic classifications and tumor characteristics")
    print(f"   📋 Generic: Extracts basic medical information")

if __name__ == "__main__":
    test_extraction_patterns()
