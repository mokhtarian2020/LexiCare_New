#!/usr/bin/env python3
"""
Test comparison with simulated different reports to show how it works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.comparator import _perform_comparison
from backend.db.session import SessionLocal
from backend.db.models import Report
from backend.db import crud
from datetime import datetime
import uuid

def test_comparison_with_different_content():
    """Test comparison with simulated different medical reports"""
    
    print("🧪 Testing LexiCare Comparison with DIFFERENT Report Content")
    print("=" * 70)
    
    # Simulate two different urine analysis reports for the same patient
    previous_report = """
ESAME CHIMICO FISICO DELLE URINE
Data: 15/01/2025
Paziente: Mario Rossi

Colore: GIALLO PAGLIERINO
Aspetto: LIMPIDO
Ph: 6.0
Glucosio: ASSENTE
Proteine: 15 mg/dl (0-10)
Emoglobina: ASSENTE  
Leucociti: 5 Leu/ul
Peso Specifico: 1.015

Risultati nella norma, lieve presenza di proteine.
"""

    current_report = """
ESAME CHIMICO FISICO DELLE URINE  
Data: 15/07/2025
Paziente: Mario Rossi

Colore: GIALLO PAGLIERINO
Aspetto: VELATO
Ph: 5.5
Glucosio: ASSENTE
Proteine: 45 * mg/dl (0-10)
Emoglobina: 0.50 * mg/dl (ASSENTE)
Leucociti: 75 * Leu/ul  
Peso Specifico: 1.020

Presenza di proteine e sangue nelle urine. Leucociti elevati.
"""

    print("📋 SIMULATED COMPARISON TEST:")
    print("\n🔸 Previous Report (January 2025):")
    print("-" * 40)
    print(previous_report.strip())
    
    print("\n🔸 Current Report (July 2025):")  
    print("-" * 40)
    print(current_report.strip())
    
    print("\n🤖 AI COMPARISON ANALYSIS:")
    print("-" * 40)
    
    try:
        comparison = _perform_comparison(previous_report, current_report)
        
        status = comparison.get('status', 'Unknown')
        explanation = comparison.get('explanation', 'No explanation provided')
        
        print(f"📊 Status: {status.upper()}")
        print(f"💬 Explanation: {explanation}")
        
        # Color coding for status
        if status.lower() == 'peggiorata':
            print("🔴 ⚠️ ALERT: Condition has WORSENED - requires medical attention")
        elif status.lower() == 'migliorata':
            print("🟢 ✅ GOOD: Condition has IMPROVED")
        elif status.lower() == 'invariata':
            print("⚪ ℹ️ INFO: Condition is UNCHANGED")
        else:
            print(f"⚠️ UNKNOWN status: {status}")
            
    except Exception as e:
        print(f"❌ Error in AI comparison: {str(e)}")
        import traceback
        traceback.print_exc()

def simulate_database_scenario():
    """Show what happens in the database when same patient uploads multiple reports"""
    
    print(f"\n{'='*70}")
    print("📊 DATABASE SCENARIO SIMULATION")
    print("=" * 70)
    
    # Get database session
    db = SessionLocal()
    
    print("""
🔍 WHAT HAPPENS WHEN YOU UPLOAD THE SAME PDF MULTIPLE TIMES:

1️⃣ FIRST UPLOAD:
   ✅ PDF parsed successfully  
   ✅ CF: SMMNNT42E67F839D found
   ✅ Report saved to database
   ❌ No previous reports found → "nessun confronto disponibile"

2️⃣ SECOND UPLOAD (same PDF):
   ✅ PDF parsed successfully
   ✅ CF: SMMNNT42E67F839D found  
   ✅ Report saved to database
   ✅ Previous report found (identical content)
   🤖 AI tries to compare identical texts
   ❌ AI gets confused → JSON parsing error

3️⃣ SOLUTION - Upload DIFFERENT medical reports:
   📄 Different exam dates
   📄 Different lab values  
   📄 Different clinical findings
   ✅ AI can provide meaningful comparison
""")
    
    # Show actual database state for the patient
    cf = "SMMNNT42E67F839D"  # CF from the urine analysis PDF
    patient_reports = crud.get_patient_reports(db, cf)
    
    print(f"\n📋 ACTUAL DATABASE STATE for CF {cf}:")
    print("-" * 50)
    print(f"Total reports found: {len(patient_reports)}")
    
    for i, report in enumerate(patient_reports, 1):
        print(f"{i}. Date: {report.report_date}, Type: {report.report_type}")
        print(f"   ID: {str(report.id)[:8]}...")
        print(f"   Text length: {len(report.extracted_text)} chars")
        if i > 1:
            # Check if content is identical to previous
            prev_text = patient_reports[i-2].extracted_text
            curr_text = report.extracted_text
            if prev_text == curr_text:
                print("   ⚠️ IDENTICAL to previous report!")
            else:
                print("   ✅ Different from previous report")
        print()
    
    db.close()

def show_frontend_behavior():
    """Explain how this appears in the frontend"""
    
    print(f"\n{'='*70}")
    print("🖥️ HOW THIS APPEARS IN THE FRONTEND")
    print("=" * 70)
    
    print("""
📱 WHEN YOU UPLOAD IDENTICAL PDFs:

╔══════════════════════════════════════════════════════════════╗
║ 📋 Referto: ESAME CHIMICO FISICO DELLE URINE               ║
║ ✅ Salvato nel database                                     ║  
║ 🔴 Errore nella comparazione: JSON parsing error           ║
║                                                              ║
║ NO "Confronto con Referti Precedenti" section shown        ║
╚══════════════════════════════════════════════════════════════╝

📱 WHEN YOU UPLOAD DIFFERENT MEDICAL REPORTS:

╔══════════════════════════════════════════════════════════════╗
║ 📋 Referto: ESAME CHIMICO FISICO DELLE URINE               ║
║ ✅ Salvato nel database                                     ║
║                                                              ║
║ 🔄 CONFRONTO CON REFERTI PRECEDENTI                         ║
║                                                              ║
║ 🔴 PEGGIORATA - Mario Rossi - Esame Urine                  ║
║    Analisi: Le proteine sono aumentate da 15 a 45 mg/dl    ║
║    e sono comparsi leucociti e sangue nelle urine,          ║
║    indicando possibile infezione o infiammazione renale.    ║
║                                                              ║
║ ⚠️ Questo risultato richiede attenzione medica immediata    ║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    test_comparison_with_different_content()
    simulate_database_scenario() 
    show_frontend_behavior()
    
    print(f"\n{'='*70}")
    print("💡 TO TEST COMPARISON PROPERLY:")
    print("1. Create different versions of medical reports (different dates/values)")
    print("2. Or use the laboratory PDFs with modified content") 
    print("3. Upload reports from the same patient but with clinical changes")
    print("✅ Then you'll see meaningful comparisons!")
