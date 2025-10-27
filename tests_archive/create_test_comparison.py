#!/usr/bin/env python3
"""
Create a test report with different values to demonstrate comparison
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.session import SessionLocal
from backend.db import crud
from datetime import datetime, timedelta
import uuid

def create_test_comparison():
    """Create a modified report for the same patient to test comparison"""
    
    print("🧪 Creating Test Report with Different Values")
    print("=" * 60)
    
    db = SessionLocal()
    
    # Use the same patient CF from your uploaded PDFs
    test_cf = "SMMNNT42E67F839D"  # Sommese Antonietta
    
    # Create a modified urine analysis report with different (worse) values
    modified_report_text = """
ESAME CHIMICO FISICO DELLE URINE
Refertato il 15/08/2025

Sig. SOMMESE ANTONIETTA
D. Nasc. 27/05/1942
C.F. SMMNNT42E67F839D

RISULTATO UNITA

Colore: GIALLO SCURO
Aspetto: TORBIDO
Ph: 5.0
Glucosio: TRACCE * mg/dl (ASSENTE)
Proteine: 75 * mg/dl (0-10)  
Emoglobina: 2.50 * mg/dl (ASSENTE)
Corpi Chetonici: PRESENTI * mg/dl (ASSENTE)
Bilirubina: TRACCE * mg/dl (ASSENTE)
Urobilinogeno: 0.8 EU/dl (0-1.0)
Peso Specifico: 1.030 (1.005-1.020)
Nitriti: POSITIVI * (Assenti)
Esterasi Leucocitaria: 500 * Leu/ul

COMMENTO:
Presenza significativa di proteine, sangue e leucociti nelle urine.
Nitriti positivi suggeriscono infezione batterica.
Peso specifico elevato indica concentrazione urinaria aumentata.
Si consiglia controllo medico urgente.
"""

    try:
        # Create the modified report
        new_report = crud.create_report(
            db=db,
            patient_cf=test_cf,
            patient_name="Sommese Antonietta",
            report_type="Esame Chimico Fisico Delle Urine",  # Same type as original
            report_date=datetime.now(),  # Current date 
            file_path="test/modified_urine_analysis.pdf",
            extracted_text=modified_report_text,
            ai_diagnosis="Infezione urinaria con proteinuria significativa e presenza di sangue",
            ai_classification="grave"
        )
        
        print(f"✅ Created test report with ID: {new_report.id}")
        print(f"📅 Date: {new_report.report_date}")
        print(f"👤 Patient: {new_report.patient_name}")
        print(f"🔬 Type: {new_report.report_type}")
        print(f"📊 Classification: {new_report.ai_classification}")
        
        # Now test comparison
        from backend.core.comparator import compare_with_previous_report_by_title
        
        print(f"\n🔄 Testing comparison with previous reports...")
        
        comparison = compare_with_previous_report_by_title(
            db=db,
            patient_cf=test_cf,
            report_type="Esame Chimico Fisico Delle Urine",
            new_text=modified_report_text
        )
        
        print(f"\n📊 COMPARISON RESULT:")
        print(f"Status: {comparison.get('status', 'Unknown')}")
        print(f"Explanation: {comparison.get('explanation', 'No explanation')}")
        
        if comparison.get('status') == 'peggiorata':
            print("🔴 ⚠️ ALERT: Condition has WORSENED!")
        elif comparison.get('status') == 'migliorata':
            print("🟢 ✅ GOOD: Condition has IMPROVED!")
        elif comparison.get('status') == 'invariata':
            print("⚪ ℹ️ INFO: Condition is UNCHANGED")
            
        print(f"\n💡 Now if you upload a PDF for this patient with exam type")
        print(f"   'Esame Chimico Fisico Delle Urine', you'll see a proper comparison!")
        
    except Exception as e:
        print(f"❌ Error creating test report: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_comparison()
