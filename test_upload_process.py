#!/usr/bin/env python3
"""
Test script to simulate the API upload process and debug the saving issue
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
    from core.pdf_parser import extract_metadata
    from core.ai_engine import analyze_laboratory_report, analyze_text_with_medgemma
    from db.session import SessionLocal
    from db import crud
    from datetime import datetime
finally:
    # Change back to original directory
    os.chdir(original_cwd)

def test_full_upload_process():
    """Test the complete upload process for both PDFs"""
    
    print("🧪 Testing Full Upload Process")
    print("=" * 50)
    
    # Test files
    pdf_files = [
        {
            "filename": "report_2024_02_01.pdf",
            "path": "/home/amir/Documents/amir/LexiCare/report_2024_02_01.pdf"
        },
        {
            "filename": "report_2024_05_01_modified.pdf", 
            "path": "/home/amir/Documents/amir/LexiCare/report_2024_05_01_modified.pdf"
        }
    ]
    
    db = SessionLocal()
    results = []
    
    try:
        for i, pdf_info in enumerate(pdf_files, 1):
            print(f"\n📄 Processing PDF {i}: {pdf_info['filename']}")
            print("-" * 40)
            
            # Read file
            with open(pdf_info['path'], 'rb') as f:
                file_bytes = f.read()
            
            # Extract metadata
            print("🔍 Extracting metadata...")
            meta = extract_metadata(file_bytes)
            
            print(f"   Patient: {meta.get('patient_name')}")
            print(f"   CF: {meta.get('codice_fiscale')}")
            print(f"   Report Type: {meta.get('report_type')}")
            print(f"   Report Category: {meta.get('report_category')}")
            print(f"   Date: {meta.get('report_date')}")
            print(f"   Lab Values: {len(meta.get('laboratory_values', {}))}")
            
            # Check CF
            codice_fiscale = meta.get('codice_fiscale')
            if not codice_fiscale:
                print("❌ No Codice Fiscale found - would not be saved")
                results.append({
                    "filename": pdf_info['filename'],
                    "saved": False,
                    "reason": "No Codice Fiscale"
                })
                continue
            
            print(f"✅ Codice Fiscale found: {codice_fiscale}")
            
            # Run AI analysis
            print("🤖 Running AI analysis...")
            try:
                report_category = meta.get('report_category', 'laboratory')
                lab_values = meta.get('laboratory_values', {})
                
                if report_category == 'laboratory' and lab_values:
                    ai_result = analyze_laboratory_report(meta)
                else:
                    ai_result = analyze_text_with_medgemma(meta['full_text'])
                    
                print(f"   Diagnosis: {ai_result.get('diagnosis', 'N/A')[:100]}...")
                print(f"   Classification: {ai_result.get('classification', 'N/A')}")
            except Exception as e:
                print(f"❌ AI analysis failed: {e}")
                results.append({
                    "filename": pdf_info['filename'],
                    "saved": False,
                    "reason": f"AI analysis error: {e}"
                })
                continue
            
            # Parse date
            print("📅 Parsing date...")
            try:
                report_date_str = meta.get('report_date')
                if report_date_str:
                    # Support various date formats
                    date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"]
                    parsed_date = None
                    
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(report_date_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    report_dt = parsed_date if parsed_date else datetime.utcnow()
                    print(f"   Parsed date: {report_dt}")
                else:
                    report_dt = datetime.utcnow()
                    print(f"   Using current date: {report_dt}")
            except Exception as e:
                print(f"⚠️ Date parsing error: {e}, using current date")
                report_dt = datetime.utcnow()
            
            # Save PDF file
            print("💾 Saving PDF file...")
            try:
                file_path = crud.save_pdf(pdf_info['filename'], file_bytes)
                print(f"   Saved to: {file_path}")
            except Exception as e:
                print(f"❌ File saving failed: {e}")
                results.append({
                    "filename": pdf_info['filename'],
                    "saved": False,
                    "reason": f"File save error: {e}"
                })
                continue
            
            # Check for previous reports (before saving new one)
            print("🔍 Checking for previous reports...")
            try:
                report_type = meta["report_type"]
                previous_report_text = crud.get_most_recent_report_text_by_title(db, codice_fiscale, report_type)
                if previous_report_text:
                    print(f"   Found previous report of same type (length: {len(previous_report_text)} chars)")
                else:
                    print("   No previous reports found")
            except Exception as e:
                print(f"⚠️ Error checking previous reports: {e}")
                previous_report_text = None
            
            # Create database record
            print("🗄️ Creating database record...")
            try:
                rec = crud.create_report(
                    db=db,
                    patient_cf=codice_fiscale,
                    patient_name=meta["patient_name"],
                    report_type=meta["report_type"],
                    report_category=meta.get("report_category", "laboratory"),
                    report_date=report_dt,
                    file_path=file_path,
                    extracted_text=meta["full_text"],
                    ai_diagnosis=ai_result["diagnosis"],
                    ai_classification=ai_result["classification"],
                )
                db.commit()
                print(f"✅ Database record created with ID: {rec.id}")
                
                # Perform comparison if previous report exists
                comparison_result = {"status": "nessun confronto disponibile", "explanation": "Primo referto di questo tipo."}
                if previous_report_text:
                    print("📊 Performing comparison...")
                    try:
                        from core.comparator import _perform_comparison
                        comparison_result = _perform_comparison(previous_report_text, meta["full_text"])
                        print(f"   Comparison status: {comparison_result.get('status', 'unknown')}")
                    except Exception as e:
                        print(f"⚠️ Comparison failed: {e}")
                        comparison_result = {"status": "errore", "explanation": f"Errore nella comparazione: {e}"}
                
                # Update with comparison results
                crud.update_report_comparison(db, rec.id, comparison_result)
                db.commit()
                
                results.append({
                    "filename": pdf_info['filename'],
                    "saved": True,
                    "report_id": str(rec.id),
                    "diagnosis": ai_result["diagnosis"],
                    "classification": ai_result["classification"],
                    "comparison_status": comparison_result.get("status"),
                    "comparison_explanation": comparison_result.get("explanation")
                })
                print("✅ Report processing completed successfully")
                
            except Exception as e:
                print(f"❌ Database operation failed: {e}")
                db.rollback()
                results.append({
                    "filename": pdf_info['filename'],
                    "saved": False,
                    "reason": f"Database error: {e}"
                })
                continue
    
    finally:
        db.close()
    
    # Print summary
    print(f"\n📊 Processing Summary")
    print("=" * 30)
    
    for result in results:
        print(f"\n📄 {result['filename']}:")
        if result['saved']:
            print(f"   ✅ Saved successfully (ID: {result['report_id']})")
            print(f"   🤖 Diagnosis: {result['diagnosis'][:100]}...")
            print(f"   📊 Classification: {result['classification']}")
            print(f"   📈 Comparison: {result['comparison_status']}")
        else:
            print(f"   ❌ Failed: {result['reason']}")
    
    # Check database state
    print(f"\n🗄️ Final Database State")
    print("=" * 25)
    
    db = SessionLocal()
    try:
        total_reports = db.query(crud.Report).count()
        print(f"Total reports in database: {total_reports}")
        
        if total_reports > 0:
            # Check for our specific patient
            patient_reports = db.query(crud.Report).filter(
                crud.Report.patient_cf == "SMMNNT42E67F839D"
            ).order_by(crud.Report.report_date.asc()).all()
            
            print(f"Reports for patient SMMNNT42E67F839D: {len(patient_reports)}")
            for i, report in enumerate(patient_reports, 1):
                print(f"  {i}. {report.report_date.strftime('%d/%m/%Y')} - {report.report_type}")
                print(f"     Comparison: {report.comparison_to_previous or 'None'}")
    finally:
        db.close()

if __name__ == "__main__":
    test_full_upload_process()
