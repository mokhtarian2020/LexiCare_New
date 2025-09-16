#!/usr/bin/env python3
"""
Test script to simulate uploading the two PDF files sequentially
and check the comparison functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.pdf_parser import extract_metadata
from backend.core.ai_engine import analyze_text_with_medgemma, analyze_laboratory_report
from backend.core.comparator import compare_with_previous_report_by_title
from backend.db.session import SessionLocal
from backend.db import crud
from datetime import datetime

def simulate_upload_workflow():
    """Simulate the complete upload workflow with your two PDFs"""
    
    print("🧪 Simulating LexiCare Upload Workflow")
    print("=" * 50)
    
    # Your two test PDF files
    pdf_files = [
        {
            "path": "report_2024_02_01.pdf",
            "description": "February 2024 - Proteine 15 mg/dl"
        },
        {
            "path": "report_2024_05_01.pdf", 
            "description": "May 2024 - Proteine 45 mg/dl"
        }
    ]
    
    db = SessionLocal()
    
    try:
        for i, pdf_info in enumerate(pdf_files, 1):
            print(f"\n📄 UPLOAD {i}: {pdf_info['description']}")
            print("-" * 40)
            
            if not os.path.exists(pdf_info['path']):
                print(f"❌ File not found: {pdf_info['path']}")
                continue
            
            # Read and extract metadata (simulating upload)
            with open(pdf_info['path'], 'rb') as f:
                pdf_bytes = f.read()
            
            try:
                # Extract metadata
                meta = extract_metadata(pdf_bytes)
                print(f"✅ Extracted metadata:")
                print(f"   Patient: {meta.get('patient_name')}")
                print(f"   CF: {meta.get('codice_fiscale')}")
                print(f"   Report Type: {meta.get('report_type')}")
                print(f"   Date: {meta.get('report_date')}")
                print(f"   Lab Values: {len(meta.get('laboratory_values', {}))} found")
                
                # Show key lab values
                lab_values = meta.get('laboratory_values', {})
                if 'Proteine' in lab_values:
                    proteine = lab_values['Proteine']
                    print(f"   🔬 Proteine: {proteine['value']} {proteine['unit']} (Ref: {proteine['reference']})")
                
                # Run AI analysis
                print(f"\n🤖 Running AI analysis...")
                if lab_values:
                    ai_result = analyze_laboratory_report(meta)
                else:
                    ai_result = analyze_text_with_medgemma(meta['full_text'])
                
                print(f"   Diagnosis: {ai_result.get('diagnosis', 'Not available')[:100]}...")
                print(f"   Classification: {ai_result.get('classification', 'Not available')}")
                
                # Check for Codice Fiscale
                cf = meta.get('codice_fiscale')
                if not cf:
                    print(f"❌ No Codice Fiscale found - report would NOT be saved")
                    continue
                
                # Save to database
                print(f"\n💾 Saving to database...")
                
                # Parse date
                report_date_str = meta.get('report_date')
                try:
                    if '/' in report_date_str:
                        report_date = datetime.strptime(report_date_str, '%d/%m/%Y')
                    else:
                        report_date = datetime.utcnow()
                except:
                    report_date = datetime.utcnow()
                
                # Save report
                report = crud.create_report(
                    db=db,
                    patient_cf=cf,
                    patient_name=meta.get('patient_name'),
                    report_type=meta.get('report_type'),
                    report_date=report_date,
                    file_path=f"test/{pdf_info['path']}",
                    extracted_text=meta['full_text'],
                    ai_diagnosis=ai_result.get('diagnosis', 'Not available'),
                    ai_classification=ai_result.get('classification', 'Not available')
                )
                
                print(f"✅ Report saved with ID: {report.id}")
                
                # Check for comparison
                print(f"\n🔄 Checking for previous reports...")
                previous_reports = crud.get_patient_reports(db, cf, meta.get('report_type'))
                print(f"   Found {len(previous_reports)} total reports for this patient/type")
                
                if len(previous_reports) > 1:  # More than just the one we just saved
                    print(f"   🎯 Previous report exists - running comparison...")
                    
                    comparison = compare_with_previous_report_by_title(
                        db=db,
                        patient_cf=cf,
                        report_type=meta.get('report_type'),
                        new_text=meta['full_text']
                    )
                    
                    print(f"   📊 Comparison Result:")
                    print(f"      Status: {comparison.get('status', 'Unknown')}")
                    print(f"      Explanation: {comparison.get('explanation', 'No explanation')}")
                    
                    # Update report with comparison
                    crud.update_report_comparison(db, report.id, comparison)
                    
                    # Show what frontend would display
                    if comparison.get('status') == 'peggiorata':
                        print(f"   🔴 Frontend: RED alert - condition worsened!")
                    elif comparison.get('status') == 'migliorata':
                        print(f"   🟢 Frontend: GREEN - condition improved!")
                    elif comparison.get('status') == 'invariata':
                        print(f"   ⚪ Frontend: GRAY - condition unchanged")
                    else:
                        print(f"   ⚠️ Frontend: Error in comparison")
                else:
                    print(f"   ℹ️ No previous reports - no comparison section shown")
                
            except Exception as e:
                print(f"❌ Error processing PDF: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Final database state
        print(f"\n📊 FINAL DATABASE STATE:")
        print("-" * 30)
        all_reports = db.query(crud.Report).all()
        print(f"Total reports: {len(all_reports)}")
        
        for report in all_reports:
            print(f"- {report.patient_name} ({report.patient_cf})")
            print(f"  Type: {report.report_type}")
            print(f"  Date: {report.report_date}")
            print(f"  Classification: {report.ai_classification}")
            if hasattr(report, 'comparison_to_previous') and report.comparison_to_previous:
                print(f"  Comparison: {report.comparison_to_previous}")
            print()
            
    except Exception as e:
        print(f"❌ Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_upload_workflow()
