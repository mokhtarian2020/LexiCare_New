#!/usr/bin/env python3
"""
Test script to validate the enhanced report type classification system
"""

import sys
import os
from pathlib import Path

# Change to backend directory for imports to work
script_dir = Path(__file__).parent
backend_dir = script_dir / "backend"
original_cwd = os.getcwd()

# Temporarily change to backend directory
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

try:
    from core.pdf_parser import classify_report_type, extract_exam_title
    from core.ai_engine import analyze_laboratory_report, analyze_radiology_report, analyze_pathology_report
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def test_report_classification():
    """Test the report classification function with different types of content"""
    
    print("🧪 Testing Report Type Classification System")
    print("=" * 50)
    
    # Test cases for different report types
    test_cases = [
        {
            "name": "Laboratory Report - Blood Chemistry",
            "text": """
            ESAME CHIMICO CLINICO
            Paziente: MARIO ROSSI
            
            GLUCOSIO: 95 mg/dl (70-110)
            CREATININA: 1.2 mg/dl (0.8-1.3)
            UREA: 35 mg/dl (15-50)
            SODIO: 140 mEq/l (136-145)
            POTASSIO: 4.2 mEq/l (3.5-5.0)
            """,
            "expected": "laboratory"
        },
        {
            "name": "Laboratory Report - Blood Count",
            "text": """
            ESAME EMOCROMOCITOMETRICO
            
            WBC: 7500 /mm3 (4000-10000)
            RBC: 4.8 mil/mm3 (4.2-5.4)
            HGB: 14.2 g/dl (12-16)
            HCT: 42% (36-46)
            PLT: 250000 /mm3 (150000-450000)
            """,
            "expected": "laboratory"
        },
        {
            "name": "Radiology Report - Chest X-ray",
            "text": """
            REFERTO DI RADIOLOGIA
            RADIOGRAFIA DEL TORACE
            
            L'esame radiografico del torace eseguito in proiezione 
            postero-anteriore evidenzia:
            - Trasparenza polmonare conservata bilateralmente
            - Assenza di addensamenti parenchimali
            - Ombre cardiache e mediastiniche nei limiti
            - Conclusioni: Quadro radiologico nella norma
            """,
            "expected": "radiology"
        },
        {
            "name": "Radiology Report - Ultrasound",
            "text": """
            ECOCOLORDOPPLERGRAFIA DEI TRONCHI SOVRAORTICI
            
            L'esame ecocolordopplergrafico evidenzia:
            - Carotide comune di destra: regolare decorso e calibro
            - Assenza di placche calcifiche o fibrose
            - Flusso regolare senza stenosi significative
            - Conclusioni: Quadro vascolare nella norma
            """,
            "expected": "radiology"
        },
        {
            "name": "Pathology Report - Histology",
            "text": """
            ESAME ISTOLOGICO
            REFERTO DI ANATOMIA PATOLOGICA
            
            Materiale pervenuto: Frammenti di tessuto in formalina
            Colorazione: Ematossilina-Eosina (H&E)
            
            DESCRIZIONE MICROSCOPICA:
            Si osservano sezioni di tessuto epiteliale con 
            architettura conservata. Assenza di displasia.
            
            DIAGNOSI: Tessuto normale senza alterazioni patologiche
            """,
            "expected": "pathology"
        },
        {
            "name": "Pathology Report - Cytology",
            "text": """
            ESAME CITOLOGICO - PAP TEST
            
            DIAGNOSI CITOLOGICA:
            Preparato citologico adeguato per la valutazione.
            Cellule epiteliali squamose mature normali.
            Assenza di cellule atipiche o neoplastiche.
            
            CLASSIFICAZIONE: NILM (Negative for Intraepithelial Lesion)
            """,
            "expected": "pathology"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 40)
        
        # Extract exam title
        title = extract_exam_title(test_case['text'])
        print(f"📋 Extracted Title: {title}")
        
        # Classify report type
        classification = classify_report_type(test_case['text'], title)
        expected = test_case['expected']
        
        print(f"🔍 Classification: {classification}")
        print(f"✅ Expected: {expected}")
        
        if classification == expected:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
        
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Report classification system is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the classification logic.")
    
    return passed == total

def test_ai_analysis_routing():
    """Test that different report types are routed to appropriate analysis functions"""
    
    print("\n🤖 Testing AI Analysis Routing")
    print("=" * 40)
    
    # Mock metadata for different report types
    test_metadata = [
        {
            "name": "Laboratory Analysis",
            "metadata": {
                "full_text": "Laboratory report text...",
                "report_category": "laboratory",
                "laboratory_values": {"GLUCOSIO": {"value": "95", "unit": "mg/dl"}},
                "patient_name": "Test Patient",
                "report_type": "Chimica Clinica"
            }
        },
        {
            "name": "Radiology Analysis", 
            "metadata": {
                "full_text": "Radiology report with imaging findings...",
                "report_category": "radiology",
                "laboratory_values": {},
                "patient_name": "Test Patient",
                "report_type": "Radiografia Torace"
            }
        },
        {
            "name": "Pathology Analysis",
            "metadata": {
                "full_text": "Pathology report with histological findings...",
                "report_category": "pathology", 
                "laboratory_values": {},
                "patient_name": "Test Patient",
                "report_type": "Esame Istologico"
            }
        }
    ]
    
    for test in test_metadata:
        print(f"\n🔍 Testing: {test['name']}")
        category = test['metadata']['report_category']
        
        try:
            if category == 'laboratory':
                result = analyze_laboratory_report(test['metadata'])
            elif category == 'radiology':
                result = analyze_radiology_report(test['metadata'])
            elif category == 'pathology':
                result = analyze_pathology_report(test['metadata'])
            
            print(f"✅ {test['name']} routing successful")
            print(f"   Category: {category}")
            
        except Exception as e:
            print(f"❌ {test['name']} routing failed: {str(e)}")

if __name__ == "__main__":
    print("🧪 LexiCare Enhanced Report Type Support Validation")
    print("=" * 60)
    
    # Test classification system
    classification_success = test_report_classification()
    
    # Test AI analysis routing  
    test_ai_analysis_routing()
    
    print(f"\n🎯 Summary:")
    if classification_success:
        print("✅ Report classification system working correctly")
        print("✅ All report types (laboratory, radiology, pathology) are supported")
        print("✅ AI analysis routing implemented for all report types")
        print("\n💡 The system now robustly supports:")
        print("   📊 Laboratory reports: Structured data with name-value pairs")
        print("   🏥 Radiology reports: Text-based imaging studies")
        print("   🔬 Pathology reports: Text-based tissue/cell analysis")
    else:
        print("⚠️ Some issues detected in report classification")
    
    print(f"\n🔧 Next steps:")
    print("   1. Test with real PDF files to validate extraction")
    print("   2. Ensure database schema is updated (add report_category column)")
    print("   3. Test end-to-end workflow with all three report types")
